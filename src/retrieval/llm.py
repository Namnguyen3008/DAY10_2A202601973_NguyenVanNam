from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from core.config import Settings, normalized_provider, require_llm_credentials


_key_counter = 0
_model_counter = 0


def build_llm(settings: Settings, temperature: float = 0.0):
    global _key_counter, _model_counter
    provider = normalized_provider(settings)
    require_llm_credentials(settings)

    if provider == "gemini":
        keys = settings.google_api_keys or ([settings.google_api_key] if settings.google_api_key else [])
        if not keys:
            raise RuntimeError("GOOGLE_API_KEY or GOOGLE_API_KEYS is required when LLM_PROVIDER=gemini.")

        models = settings.llm_models or ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]

        api_key = keys[_key_counter % len(keys)]
        model_name = models[_model_counter % len(models)]

        _key_counter += 1
        _model_counter += 1

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
        )
    if provider == "openai":
        return ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            temperature=temperature,
        )
    if provider == "anthropic":
        return ChatAnthropic(
            model=settings.model_name,
            api_key=settings.anthropic_api_key,
            temperature=temperature,
        )
    if provider == "openrouter":
        return ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=temperature,
        )
    if provider == "ollama":
        return ChatOllama(
            model=settings.model_name,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )
    if provider == "custom":
        return ChatOpenAI(
            model=settings.model_name,
            api_key=settings.custom_llm_api_key or "unused",
            base_url=settings.custom_llm_base_url,
            temperature=temperature,
        )
    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")
