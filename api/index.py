"""
Blitz TokyoInsider Scraper API — Vercel serverless entry
Author: Blitz (@blitzlabx)

Vercel Python runtime loads this ASGI app.
Native deps (curl_cffi, lxml) may not build on every Vercel region —
prefer Render or Docker for production reliability.
"""
from app.main import app  # noqa: F401
