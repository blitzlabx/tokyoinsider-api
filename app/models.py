"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
from pydantic import BaseModel, Field


class DownloadFile(BaseModel):
    filename: str
    url: str | None = None
    size: str | None = None
    downloads: str | None = None
    uploader: str | None = None
    added_on: str | None = None
    comments_url: str | None = None
    error: str | None = None


class DownloadItem(BaseModel):
    kind: str | None = None
    number: int | None = None
    label: str | None = None
    filename: str | None = None
    url: str | None = None
    page_url: str | None = None
    error: str | None = None


class Genre(BaseModel):
    name: str | None = None
    url: str | None = None


class AnimeRef(BaseModel):
    title: str | None = None
    url: str | None = None


class AnimeDetail(BaseModel):
    title: str | None = None
    titles: list[str] = Field(default_factory=list)
    slug: str | None = None
    letter: str | None = None
    url: str | None = None
    cover: str | None = None
    rss: str | None = None
    creator: str | None = None
    genres: list[Genre] = Field(default_factory=list)
    age_group: str | None = None
    vintage: str | None = None
    status: str | None = None
    summary: str | None = None
    ratings: dict[str, str] = Field(default_factory=dict)
    related: list[AnimeRef] = Field(default_factory=list)
    downloads: list[DownloadItem] = Field(default_factory=list)
    pagination: dict = Field(default_factory=dict)


class EpisodeDetail(BaseModel):
    heading: str | None = None
    kind: str | None = None
    number: int | None = None
    files: list[DownloadFile] = Field(default_factory=list)
    prev: str | None = None
    next: str | None = None
    prev_url: str | None = None
    next_url: str | None = None


class SearchResult(BaseModel):
    title: str | None = None
    url: str | None = None
    letter: str | None = None
    slug: str | None = None
    cover: str | None = None
    score: float | None = None


class CatalogEntry(BaseModel):
    title: str
    url: str
    letter: str
    slug: str
