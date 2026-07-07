from __future__ import annotations

from .mock_provider import MockMarketProvider


class AKShareProvider(MockMarketProvider):
    """AKShare provider placeholder.

    The dependency is intentionally not imported here yet. When AKShare is
    added, only this provider should change; Repository, Domain, Application,
    API, and Frontend contracts should remain stable.
    """

    name = "akshare"
