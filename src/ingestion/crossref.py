from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import time
from typing import Any

import requests

from core.config import Settings
from core.utils import ensure_parent, normalize_whitespace, read_json, write_json


@dataclass(frozen=True)
class PaperRecord:
    """Represents a structured academic paper record extracted from the Crossref API."""
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_abstract(raw_abstract: str) -> str:
    if not raw_abstract:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", raw_abstract)
    cleaned = re.sub(r"^abstract\s*:?", "", cleaned, flags=re.IGNORECASE)
    return normalize_whitespace(cleaned)


def _format_date(date_struct: dict | None) -> str:
    if not date_struct or "date-parts" not in date_struct or not date_struct["date-parts"]:
        return "2024-01-01"
    parts = date_struct["date-parts"][0]
    year = parts[0] if len(parts) > 0 else 2024
    month = parts[1] if len(parts) > 1 else 1
    day = parts[2] if len(parts) > 2 else 1
    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        doi = item.get("DOI", "").strip()
        if not doi:
            continue
        
        titles = item.get("title", [])
        title = normalize_whitespace(titles[0]) if titles else ""
        if not title:
            continue

        raw_abstract = item.get("abstract", "")
        summary = _clean_abstract(raw_abstract)

        authors: list[str] = []
        for author in item.get("author", []):
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            name = author.get("name", "").strip()
            full_name = f"{given} {family}".strip() if (given or family) else name
            if full_name:
                authors.append(full_name)
        if not authors:
            authors = ["Unknown Author"]

        categories = item.get("subject", [])
        if not categories:
            categories = ["Computer Science", "Artificial Intelligence"]
        primary_category = categories[0]

        pub_struct = item.get("published-online") or item.get("published-print") or item.get("issued") or item.get("created")
        published = _format_date(pub_struct)

        upd_struct = item.get("deposited") or item.get("indexed") or pub_struct
        updated = _format_date(upd_struct)

        abs_url = item.get("URL") or f"https://doi.org/{doi}"
        
        pdf_url = ""
        link_list = item.get("link", [])
        for link in link_list:
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", "")
                break
        if not pdf_url:
            pdf_url = abs_url

        comment = item.get("publisher", "")

        records.append(
            PaperRecord(
                paper_id=doi,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    if not settings.refresh_source and settings.paths.raw_records_json.exists():
        return load_raw_records(settings.paths.raw_records_json)

    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {
        "User-Agent": "Day10DataPipelineLab/1.0 (mailto:student@example.com)"
    }

    max_retries = 3
    backoff = 2.0
    payload: dict[str, Any] = {}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code in (429, 503, 504):
                time.sleep(backoff * (attempt + 1))
                continue
            response.raise_for_status()
            payload = response.json()
            break
        except Exception as exc:
            if attempt == max_retries - 1:
                if settings.paths.raw_api_response.exists():
                    payload = read_json(settings.paths.raw_api_response)
                else:
                    raise RuntimeError(f"Failed to fetch Crossref records after {max_retries} attempts: {exc}")
            time.sleep(backoff * (attempt + 1))

    if payload:
        write_json(settings.paths.raw_api_response, payload)

    records = parse_crossref_payload(payload)
    
    serialized_records = [asdict(record) for record in records]
    write_json(settings.paths.raw_records_json, serialized_records)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    raw_list = read_json(path)
    records: list[PaperRecord] = []
    for item in raw_list:
        records.append(
            PaperRecord(
                paper_id=item["paper_id"],
                title=item["title"],
                summary=item["summary"],
                authors=item.get("authors", []),
                categories=item.get("categories", []),
                primary_category=item.get("primary_category", "Uncategorized"),
                published=item.get("published", "2024-01-01"),
                updated=item.get("updated", "2024-01-01"),
                abs_url=item.get("abs_url", ""),
                pdf_url=item.get("pdf_url", ""),
                comment=item.get("comment", ""),
            )
        )
    return records

