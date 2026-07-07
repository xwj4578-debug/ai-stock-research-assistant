from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MarketProvider(ABC):
    """External market data adapter contract.

    Providers only fetch or adapt source data. They must not contain AlphaLens
    scoring, ranking, or research workflow logic.
    """

    name = "base"

    @abstractmethod
    def get_market_overview(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_hot_sectors(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_market_news(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_limit_statistics(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_candidates(self) -> list[dict[str, Any]]:
        raise NotImplementedError
