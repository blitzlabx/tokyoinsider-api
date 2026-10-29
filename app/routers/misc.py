import httpx
from fastapi import APIRouter, Query

from ..catalog import load_catalog
from ..errors import UpstreamError
from ..fetch import fetcher
from ..parse import parse_search

router = APIRouter(prefix="/api/v1", tags=["misc"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/browse")
async def browse(letter: str = Query(..., min_length=1, max_length=1)):
    base, html = await fetcher.get(f"/anime/{letter.upper()}")
    return parse_search(html, base)


@router.get("/media-check")
async def media_check(url: str):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.head(url, headers={"User-Agent": "Mozilla/5.0"})
        return {"url": url, "status": resp.status_code, "alive": resp.status_code < 400}
    except Exception as exc:  # noqa: BLE001
        raise UpstreamError(f"media check failed: {exc}") from exc
