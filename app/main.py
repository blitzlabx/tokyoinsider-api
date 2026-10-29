"""
Blitz TokyoInsider Scraper API
==============================
Created & maintained by Blitz (@blitzlabx)

A free, CORS-enabled JSON API that turns tokyoinsider.net / .com / .org
into clean, structured endpoints for anime metadata and download links.

Author  : Blitz
Handle  : @blitzlabx
GitHub  : https://github.com/blitzlabx
Site    : https://blitz.devs.surf
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .errors import UpstreamError
from .fetch import fetcher
from .routers import anime, catalog, downloads, latest, misc, search

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Blitz TokyoInsider Scraper API",
    version="1.0.0",
    description=(
        "Free CORS-enabled scraper for tokyoinsider.net / .com / .org. "
        "Built and maintained by Blitz (@blitzlabx). "
        "All rights and credits belong to Blitz / blitzlabx."
    ),
    contact={
        "name": "Blitz",
        "url": "https://github.com/blitzlabx",
        "email": "blitz@blitzlabx",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


@app.exception_handler(UpstreamError)
async def upstream_handler(_: Request, exc: UpstreamError):
    return JSONResponse(
        status_code=exc.status, content={"error": exc.code, "detail": str(exc)}
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    await fetcher.close()


for module in (anime, catalog, downloads, latest, misc, search):
    app.include_router(module.router)


@app.get("/")
async def root():
    return {
        "name": "Blitz TokyoInsider Scraper API",
        "version": "1.0.0",
        "author": "Blitz",
        "handle": "@blitzlabx",
        "github": "https://github.com/blitzlabx",
        "docs": "/docs",
        "credits": "All credits to Blitz (@blitzlabx)",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "blitz-tokyoinsider-api", "author": "Blitz"}
