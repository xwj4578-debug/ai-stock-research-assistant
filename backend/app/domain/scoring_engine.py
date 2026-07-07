from __future__ import annotations

from typing import Any

from .config_loader import load_domain_config


class ScoringEngine:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or load_domain_config("scoring.yaml")

    def explain_score(self, item: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        weights: dict[str, Any] = self.config["weights"]
        field_map: dict[str, str] = self.config["field_map"]
        max_input = self.config["normalization"]["max_input_score"]
        min_input = self.config["normalization"]["min_input_score"]
        details: dict[str, int] = {}
        reasons: dict[str, str] = {}
        for dimension, weight in weights.items():
            value = self._dimension_value(dimension, field_map.get(dimension), item, context)
            normalized = self._normalize(value, min_input, max_input)
            score = round(normalized * float(weight))
            details[dimension] = score
            reasons[dimension] = self._reason(dimension, value, score, weight)
        total = sum(details.values())
        return {"totalScore": total, "details": details, "reasons": reasons}

    def _dimension_value(self, dimension: str, field: str | None, item: dict[str, Any], context: dict[str, Any]) -> float:
        if dimension == "market":
            return float(context.get("market_score") or item.get(field or "") or 0)
        if dimension == "sector":
            return float(context.get("heat_score") or item.get(field or "") or 0)
        value = item.get(field or "")
        if dimension == "risk":
            risk = float(value or 0)
            return max(0.0, 100.0 - risk)
        return float(value or 0)

    @staticmethod
    def _normalize(value: float, min_input: float, max_input: float) -> float:
        if max_input <= min_input:
            return 0.0
        return max(0.0, min(1.0, (value - min_input) / (max_input - min_input)))

    @staticmethod
    def _reason(dimension: str, value: float, score: int, weight: float) -> str:
        return f"{dimension} uses input {round(value, 2)} and contributes {score}/{weight}."
