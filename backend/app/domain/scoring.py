from __future__ import annotations

from typing import Any

from .recommendation_engine import RecommendationEngine
from .risk_engine import RiskEngine

_risk_engine = RiskEngine()
_recommendation_engine = RecommendationEngine()

def risk_level(score: Any) -> str:
    return _risk_engine.level(score)


def next_action(item: dict[str, Any]) -> str:
    return _recommendation_engine.next_action(item)
