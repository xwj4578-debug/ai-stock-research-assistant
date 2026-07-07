from __future__ import annotations

from typing import Any

from .mock_provider import MockMarketProvider


class EastMoneyProvider(MockMarketProvider):
    """Placeholder provider boundary for EastMoney.

    Existing quote fetchers already use public EastMoney-style endpoints in
    other modules. Sprint 05 only establishes the replaceable provider shape,
    so this adapter currently falls back to the mock-normalized provider.
    """

    name = "eastmoney"

    def get_market_overview(self) -> dict[str, Any]:
        data = super().get_market_overview()
        return {**data, "provider": self.name}
