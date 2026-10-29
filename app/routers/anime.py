from fastapi import APIRouter

from ..fetch import fetcher
from ..models import AnimeDetail, EpisodeDetail
from ..parse import parse_anime, parse_episode, parse_listing_downloads, parse_pagination

router = APIRouter(prefix="/api/v1/anime", tags=["anime"])


@router.get("/{letter}/{slug}", response_model=AnimeDetail)
async def detail(letter: str, slug: str):
    base, html = await fetcher.get(f"/anime/{letter}/{slug}")
    downloads = parse_listing_downloads(html, base)
    for item in downloads:
        if item.get("page_url"):
            item["page_url"] = item["page_url"].format(letter=letter, name=slug)
    return AnimeDetail(
        slug=slug,
        letter=letter,
        url=f"{base}/anime/{letter}/{slug}",
        downloads=downloads,
        pagination=parse_pagination(html),
        **parse_anime(html, base),
    )


@router.get("/{letter}/{slug}/{kind}/{number}", response_model=EpisodeDetail)
async def episode(letter: str, slug: str, kind: str, number: int):
    _base, html = await fetcher.get(f"/anime/{letter}/{slug}/{kind.lower()}/{number}")
    return EpisodeDetail(kind=kind.lower(), number=number, **parse_episode(html))
