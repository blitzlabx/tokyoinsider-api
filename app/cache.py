"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
import asyncio
import time
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock(self, key: str) -> asyncio.Lock:
        return self._locks.setdefault(key, asyncio.Lock())

    async def get_or_set(self, key: str, ttl: float, factory):
        entry = self._data.get(key)
        now = time.monotonic()
        if entry and entry[0] > now:
            return entry[1]
        async with self._lock(key):
            entry = self._data.get(key)
            now = time.monotonic()
            if entry and entry[0] > now:
                return entry[1]
            value = await factory()
            self._data[key] = (now + ttl, value)
            return value

    def invalidate(self, prefix: str = "") -> None:
        for key in [k for k in self._data if k.startswith(prefix)]:
            self._data.pop(key, None)
