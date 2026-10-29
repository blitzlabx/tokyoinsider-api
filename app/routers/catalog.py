from fastapi import APIRouter, Query

from ..catalog import load_catalog
from ..models import CatalogEntry

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get("/catalog", response_model=list[CatalogEntry])
async def catalog(letter: str | None = Query(None, max_length=1)):
    entries = await load_catalog()
    if letter:
        entries = [e for e in entries if e.letter.upper() == letter.upper()]
    return entries


@router.get("/catalog/count")
async def catalog_count():
    return {"count": len(await load_catalog())}
