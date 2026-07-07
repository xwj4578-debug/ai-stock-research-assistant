from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..providers import MarketProvider, MockMarketProvider
from .cache_repository import MemoryCacheRepository


class MarketRepository:
    """Stable normalized data boundary for Domain services."""

    def __init__(
        self,
        provider: MarketProvider,
        fallback_provider: MarketProvider | None = None,
        cache: MemoryCacheRepository | None = None,
        retries: int = 1,
    ) -> None:
        self.provider = provider
        self.fallback_provider = fallback_provider or MockMarketProvider()
        self.cache = cache or MemoryCacheRepository()
        self.retries = retries

    def get_market_overview(self) -> dict[str, Any]:
        return self._cached("market_overview", self.provider.get_market_overview, self.fallback_provider.get_market_overview)

    def get_hot_sectors(self) -> list[dict[str, Any]]:
        return self._cached("hot_sectors", self.provider.get_hot_sectors, self.fallback_provider.get_hot_sectors)

    def get_market_news(self) -> list[dict[str, Any]]:
        return self._cached("market_news", self.provider.get_market_news, self.fallback_provider.get_market_news)

    def get_limit_statistics(self) -> dict[str, Any]:
        return self._cached("limit_statistics", self.provider.get_limit_statistics, self.fallback_provider.get_limit_statistics)

    def get_candidates(self) -> list[dict[str, Any]]:
        return self._cached("candidates", self.provider.get_candidates, self.fallback_provider.get_candidates)

    def _cached(self, key: str, fn: Callable[[], Any], fallback: Callable[[], Any]) -> Any:
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        value = self._retry(fn, fallback)
        self.cache.set(key, value)
        return value

    def _retry(self, fn: Callable[[], Any], fallback: Callable[[], Any]) -> Any:
        last_error: Exception | None = None
        for _ in range(self.retries + 1):
            try:
                return fn()
            except Exception as error:  # pragma: no cover - defensive provider boundary
                last_error = error
        try:
            return fallback()
        except Exception:
            if last_error:
                raise last_error
            raise
