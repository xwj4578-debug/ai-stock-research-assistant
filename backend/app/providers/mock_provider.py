from __future__ import annotations

from typing import Any

from .base import MarketProvider
from ..radar import build_market_radar


class MockMarketProvider(MarketProvider):
    name = "mock"

    def __init__(self) -> None:
        self._cached_radar: dict[str, Any] | None = None

    def _radar(self) -> dict[str, Any]:
        if self._cached_radar is None:
            self._cached_radar = build_market_radar()
        return self._cached_radar

    def get_market_overview(self) -> dict[str, Any]:
        return self._radar().get("market", {})

    def get_hot_sectors(self) -> list[dict[str, Any]]:
        return self._radar().get("sectors", [])

    def get_market_news(self) -> list[dict[str, Any]]:
        sectors = self.get_hot_sectors()
        return [
            {
                "title": f"{item.get('name')} heat score {item.get('heat_score')}",
                "source": "mock",
                "relatedSector": item.get("name"),
            }
            for item in sectors[:5]
        ]

    def get_limit_statistics(self) -> dict[str, Any]:
        stats = self._radar().get("market", {}).get("stats", {})
        return {
            "limitUp": stats.get("limit_up_count"),
            "limitDown": stats.get("limit_down_count"),
            "failedLimitRate": stats.get("failed_limit_rate"),
        }

    def get_candidates(self) -> list[dict[str, Any]]:
        return self._radar().get("candidates", [])
