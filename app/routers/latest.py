from fastapi import APIRouter, Query

from ..fetch import fetcher
from ..models import DownloadItem
from ..parse import parse_new

router = APIRouter(prefix="/api/v1", tags=["latest"])


@router.get("/latest", response_model=list[DownloadItem])
async def latest(page: int = Query(1, ge=1, le=200)):
    path = "/new" if page == 1 else f"/new?start={(page - 1) * 30}"
    base, html = await fetcher.get(path)
    return parse_new(html, base)


@router.get("/home", response_model=list[DownloadItem])
async def home():
    base, html = await fetcher.get("/")
    return parse_new(html, base)
