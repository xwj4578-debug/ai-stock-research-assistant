from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class MemoryCacheRepository:
    def __init__(self) -> None:
        self._items: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._items.get(key)
        if not entry:
            return None
        if entry.expires_at < monotonic():
            self._items.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        self._items[key] = CacheEntry(value=value, expires_at=monotonic() + ttl_seconds)
