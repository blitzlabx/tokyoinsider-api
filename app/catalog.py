"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
import re

from rapidfuzz import fuzz

from .config import settings
from .fetch import fetcher
from .models import CatalogEntry

_CATALOG_PATH = "/upload/autocomplete.js"
_ENTRY_RE = re.compile(r'\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*"([^"]+)"\s*\]')
_cache: list[CatalogEntry] | None = None


async def load_catalog() -> list[CatalogEntry]:
    global _cache
    if _cache is not None:
        return _cache
    _url, body = await fetcher.get(_CATALOG_PATH)
    entries: list[CatalogEntry] = []
    for title, path in _ENTRY_RE.findall(body):
        title = title.replace('\\"', '"').replace("\\\\", "\\")
        slug = path.rstrip("/").rsplit("/", 1)[-1]
        match = re.search(r"/anime/([^/])/", path)
        letter = match.group(1) if match else (title[:1].upper() or "A")
        entries.append(
            CatalogEntry(
                title=title,
                url=f"{settings.base_url}/anime/{letter}/{slug}",
                letter=letter,
                slug=slug,
            )
        )
    _cache = entries
    return entries


def local_search(entries: list[CatalogEntry], query: str, limit: int) -> list[dict]:
    scored = []
    for entry in entries:
        score = max(
            fuzz.WRatio(query, entry.title),
            fuzz.partial_ratio(query.lower(), entry.title.lower()),
        )
        if score >= 60:
            scored.append({**entry.model_dump(), "score": round(score, 1)})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
