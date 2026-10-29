from fastapi import APIRouter

from ..fetch import fetcher
from ..models import DownloadItem, EpisodeDetail
from ..parse import parse_episode, parse_listing_downloads

router = APIRouter(prefix="/api/v1/download", tags=["downloads"])


@router.get("/{letter}/{slug}", response_model=list[DownloadItem])
async def all_links(letter: str, slug: str):
    base, html = await fetcher.get(f"/anime/{letter}/{slug}")
    items = parse_listing_downloads(html, base)
    for item in items:
        if item.get("page_url"):
            item["page_url"] = item["page_url"].format(letter=letter, name=slug)
    return items


@router.get("/{letter}/{slug}/{kind}/{number}", response_model=EpisodeDetail)
async def episode_links(letter: str, slug: str, kind: str, number: int):
    _base, html = await fetcher.get(f"/anime/{letter}/{slug}/{kind.lower()}/{number}")
    return EpisodeDetail(kind=kind.lower(), number=number, **parse_episode(html))
