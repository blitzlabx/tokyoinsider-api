from fastapi import APIRouter, Query

from ..catalog import load_catalog, local_search
from ..fetch import fetcher
from ..models import SearchResult
from ..parse import parse_search

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/suggest", response_model=list[SearchResult])
async def suggest(q: str = Query(..., min_length=1), limit: int = Query(15, ge=1, le=50)):
    return local_search(await load_catalog(), q, limit)


@router.get("/search", response_model=list[SearchResult])
async def search(
    q: str = Query(..., min_length=1),
    start: int = Query(0, ge=0),
    status: str | None = None,
    author: str | None = None,
    genres: str | None = None,
    rating: str | None = None,
):
    form = {"search[keyword]": q, "start": str(start)}
    if status:
        form["search[status]"] = status
    if author:
        form["search[author]"] = author
    if genres:
        form["search[genres]"] = genres
    if rating:
        form["search[rating]"] = rating
    base, html = await fetcher.get("/anime/search", data=form)
    results = parse_search(html, base)
    if results:
        return results
    return local_search(await load_catalog(), q, 50)
