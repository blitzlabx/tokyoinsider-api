"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
import asyncio
import random
import time

import httpx
from curl_cffi.requests import AsyncSession

from .config import settings
from .errors import UpstreamBlocked, UpstreamError

CF_MARKERS = ("Just a moment", "cf-challenge", "cf_chl_opt", "Attention Required")


def _looks_blocked(status: int, body: str) -> bool:
    if status in (403, 429, 503):
        return True
    head = body[:4000]
    return any(marker in head for marker in CF_MARKERS)


class Fetcher:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._last = 0.0
        self._curl: AsyncSession | None = None
        self._httpx: httpx.AsyncClient | None = None

    async def _throttle(self) -> None:
        async with self._lock:
            delta = time.monotonic() - self._last
            wait = settings.min_interval - delta
            if wait > 0:
                await asyncio.sleep(wait + random.uniform(0, 0.1))
            self._last = time.monotonic()

    def _headers(self, base: str) -> dict[str, str]:
        return {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": base + "/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        }

    @staticmethod
    def _origin(url: str) -> str:
        parts = url.split("/", 3)
        return parts[0] + "//" + parts[2]

    async def _via_curl(self, url: str, data: dict | None) -> tuple[int, str]:
        if self._curl is None:
            self._curl = AsyncSession(
                impersonate=settings.impersonate,
                proxy=settings.proxy,
                timeout=settings.timeout,
            )
        resp = await self._curl.request(
            "POST" if data else "GET",
            url,
            data=data,
            headers=self._headers(self._origin(url)),
            allow_redirects=True,
        )
        return resp.status_code, resp.text

    async def _via_httpx(self, url: str, data: dict | None) -> tuple[int, str]:
        if self._httpx is None:
            self._httpx = httpx.AsyncClient(
                follow_redirects=True, timeout=settings.timeout, proxy=settings.proxy
            )
        resp = await self._httpx.request(
            "POST" if data else "GET",
            url,
            data=data,
            headers=self._headers(self._origin(url)),
        )
        return resp.status_code, resp.text

    async def _via_flaresolverr(self, url: str) -> str:
        if not settings.flaresolverr_url:
            raise UpstreamBlocked("challenge present and no FlareSolverr configured")
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                settings.flaresolverr_url.rstrip("/") + "/v1",
                json={"cmd": "request.get", "url": url, "maxTimeout": 60000},
            )
            payload = resp.json()
        if payload.get("status") != "ok":
            raise UpstreamBlocked(f"FlareSolverr failed: {payload.get('message')}")
        return payload["solution"]["response"]

    async def get(self, path: str, *, data: dict | None = None) -> tuple[str, str]:
        path = path if path.startswith("/") else "/" + path
        bases = [settings.base_url] + [m for m in settings.mirrors if m != settings.base_url]
        last: Exception | None = None

        for base in bases:
            url = base.rstrip("/") + path
            for attempt in range(settings.max_retries):
                await self._throttle()
                try:
                    status, body = await self._via_curl(url, data)
                except Exception as exc:  # noqa: BLE001
                    last = UpstreamError(f"transport error: {exc}")
                    await asyncio.sleep(settings.retry_base * (2 ** attempt))
                    continue

                if status == 404:
                    last = UpstreamError("404 from upstream")
                    break
                if status >= 400 or _looks_blocked(status, body):
                    if _looks_blocked(status, body):
                        try:
                            return url, await self._via_flaresolverr(url)
                        except UpstreamError as exc:
                            last = exc
                    else:
                        last = UpstreamError(f"HTTP {status}")
                    await asyncio.sleep(settings.retry_base * (2 ** attempt))
                    continue
                if not body.strip():
                    last = UpstreamError("empty body")
                    await asyncio.sleep(settings.retry_base * (2 ** attempt))
                    continue
                return url, body

        for base in bases:
            url = base.rstrip("/") + path
            try:
                status, body = await self._via_httpx(url, data)
                if status < 400 and body.strip():
                    return url, body
            except Exception as exc:  # noqa: BLE001
                last = UpstreamError(str(exc))
        raise last or UpstreamError("all mirrors failed")

    async def close(self) -> None:
        if self._curl is not None:
            await self._curl.close()
        if self._httpx is not None:
            await self._httpx.aclose()


fetcher = Fetcher()
