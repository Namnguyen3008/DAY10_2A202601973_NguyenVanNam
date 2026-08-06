from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import itertools
import time


from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import requests
from sentence_transformers import SentenceTransformer

from core.config import Settings




@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = _load_model(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


from requests.adapters import HTTPAdapter

_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=32, pool_maxsize=32)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


class MultiKeyMistralEmbeddings(Embeddings):
    def __init__(self, api_keys: list[str], model_name: str = "mistral-embed"):
        self.api_keys = api_keys
        self.model_name = model_name
        self.url = "https://api.mistral.ai/v1/embeddings"

    def _embed_batch(self, args: tuple[str, list[str]]) -> list[list[float]]:
        key, batch = args
        if not batch:
            return []
        
        max_retries = 5
        key_cycle = itertools.cycle(self.api_keys)
        current_key = key

        for attempt in range(max_retries):
            headers = {"Authorization": f"Bearer {current_key}"}
            payload = {"model": self.model_name, "input": batch}
            try:
                res = _session.post(self.url, headers=headers, json=payload, timeout=15)
                if res.status_code in (429, 503, 504):
                    current_key = next(key_cycle)
                    time.sleep(0.3 * (attempt + 1))
                    continue
                res.raise_for_status()
                data = res.json()["data"]
                sorted_data = sorted(data, key=lambda x: x["index"])
                return [item["embedding"] for item in sorted_data]
            except Exception as exc:
                if attempt == max_retries - 1:
                    raise exc
                current_key = next(key_cycle)
                time.sleep(0.3 * (attempt + 1))
        return []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        batch_size = 50
        key_cycle = itertools.cycle(self.api_keys)
        tasks = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            key = next(key_cycle)
            tasks.append((key, chunk))
        
        if len(tasks) == 1:
            return self._embed_batch(tasks[0])
            
        with ThreadPoolExecutor(max_workers=min(len(tasks), 16)) as executor:
            results = list(executor.map(self._embed_batch, tasks))
        return [emb for sublist in results for emb in sublist]

    def embed_query(self, text: str) -> list[float]:
        results = self.embed_documents([text])
        return results[0]


def get_embeddings(settings: Settings) -> Embeddings:
    model_name = settings.embedding_model
    if "mistral" in model_name.lower():
        return MultiKeyMistralEmbeddings(
            api_keys=settings.mistral_api_keys,
            model_name="mistral-embed",
        )
    if "gemini" in model_name.lower() or "google" in model_name.lower() or model_name.startswith("models/"):
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=settings.google_api_key,
        )
    return MiniLMEmbeddings(model_name)


