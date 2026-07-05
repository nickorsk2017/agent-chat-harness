"""Simple in-memory cache for doc_analyzer (swap for Redis/SQLite in prod)."""

from __future__ import annotations

import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_s: float = 300.0) -> None:
        self._ttl = ttl_s
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        hit = self._store.get(key)
        if not hit:
            return None
        ts, value = hit
        if time.monotonic() - ts > self._ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic(), value)


cache = TTLCache()
