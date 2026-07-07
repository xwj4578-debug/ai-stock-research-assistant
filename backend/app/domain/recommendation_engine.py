from __future__ import annotations

from typing import Any

from .config_loader import load_domain_config


class RecommendationEngine:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or load_domain_config("recommendation.yaml")

    def next_action(self, item: dict[str, Any]) -> str:
        thresholds = self.config["thresholds"]
        actions = self.config["next_action"]
        if (item.get("risk_score") or 0) >= thresholds["high_risk"]:
            return actions["high_risk"]
        if (item.get("buy_point_score") or 0) >= thresholds["buy_signal"]:
            return actions["buy_signal"]
        return actions["default"]

    def explain(self, action: str) -> str:
        return self.config["templates"].get(action, self.config["templates"]["observe"])
