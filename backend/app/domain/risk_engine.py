from __future__ import annotations

from typing import Any

from .config_loader import load_domain_config


class RiskEngine:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or load_domain_config("risk.yaml")

    def level(self, score: Any) -> str:
        numeric = float(score or 0)
        levels = self.config["levels"]
        ordered = sorted(levels.values(), key=lambda item: item["min"], reverse=True)
        for item in ordered:
            if numeric >= item["min"]:
                return item["label"]
        return ordered[-1]["label"]

    def signals(self, item: dict[str, Any]) -> list[str]:
        score = float(item.get("risk_score") or 0)
        messages = []
        for rule in self.config["signals"].values():
            if score >= rule["threshold"]:
                messages.append(rule["message"])
        return messages
