from __future__ import annotations

from datetime import datetime
from typing import Any

from ..repository import MarketRepository
from .ranking import rank_research_queue, rank_sector_leaders
from .recommendation_engine import RecommendationEngine
from .risk_engine import RiskEngine
from .scoring import next_action, risk_level
from .scoring_engine import ScoringEngine


class ResearchEngine:
    """AlphaLens domain logic.

    This layer depends on Repository abstractions and normalized dictionaries.
    It must not import provider SDKs or call external data sources directly.
    """

    def __init__(self, repository: MarketRepository) -> None:
        self.repository = repository
        self.scoring_engine = ScoringEngine()
        self.risk_engine = RiskEngine()
        self.recommendation_engine = RecommendationEngine()

    def build_workspace_model(self) -> dict[str, Any]:
        market = self.repository.get_market_overview()
        sectors = self.repository.get_hot_sectors()
        candidates = self.repository.get_candidates()
        hot_sectors = [self._build_hot_sector(item, candidates) for item in sectors]
        queue = [self._enrich_candidate(row, market, hot_sectors) for row in rank_research_queue(candidates)]
        risks = [self._build_risk_alert(item) for item in queue if (item.get("risk_score") or 0) >= 70][:6]
        summary = self._build_summary(market, hot_sectors, queue, risks)
        return {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "marketPulse": market,
            "dailyBrief": summary,
            "researchQueue": queue,
            "hotSectors": hot_sectors,
            "watchlist": [],
            "riskAlerts": risks,
            "raw": {
                "market": market,
                "sectors": hot_sectors,
                "candidates": candidates,
                "summary": {
                    "focus_count": len(queue),
                    "buy_signal_count": len([item for item in queue if (item.get("buy_point_score") or 0) >= 65]),
                    "risk_count": len(risks),
                    "focus_directions": [item.get("name") for item in hot_sectors[:3]],
                    "suggestion": summary,
                },
            },
        }

    def list_watchlist_candidates(self) -> list[dict[str, Any]]:
        market = self.repository.get_market_overview()
        sectors = self.repository.get_hot_sectors()
        heat_by_name = {item.get("name"): item.get("heat_score") for item in sectors}
        return [
            {
                "id": row.get("code"),
                "stockCode": row.get("code"),
                "name": row.get("name"),
                "score": row.get("research_score", row.get("overall_score")),
                "riskLevel": risk_level(row.get("risk_score")),
                "nextAction": next_action(row),
                "lastAnalysis": datetime.now().isoformat(timespec="seconds"),
                "changeSummary": row.get("candidate_reason"),
                "scoreDetails": row.get("score_details"),
            }
            for row in [self._enrich_candidate(candidate, market, [], heat_by_name) for candidate in rank_research_queue(self.repository.get_candidates())]
        ]

    def find_candidate(self, code: str) -> dict[str, Any] | None:
        return next((row for row in self.repository.get_candidates() if str(row.get("code")) == code), None)

    def _build_hot_sector(self, item: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
        members = [
            row
            for row in candidates
            if row.get("industry") == item.get("name") or item.get("name") in str(row.get("candidate_reason", ""))
        ]
        leaders = rank_sector_leaders(members)
        core = leaders[1] if len(leaders) > 1 else leaders[0] if leaders else None
        leader_name = item.get("leader") or (leaders[0]["name"] if leaders else "")
        core_name = core["name"] if core else leader_name
        reason = item.get("conclusion") or item.get("catalyst") or "Hot sector needs continued confirmation."
        return {
            "name": item.get("name"),
            "change_pct": item.get("change_pct"),
            "heat_score": item.get("heat_score"),
            "amount_yi": item.get("amount_yi"),
            "main_net_inflow_yi": item.get("main_net_inflow_yi"),
            "limit_up_count": item.get("limit_up_count"),
            "leader": leader_name,
            "trend_core": core_name,
            "ai_summary": reason,
            "members": members[:12],
            "leader_rank": leaders,
            "fund_flow": item.get("main_net_inflow_yi"),
            "news": [
                f"{item.get('name')} heat score {item.get('heat_score')}.",
                f"Leader: {leader_name}; trend core: {core_name}.",
            ],
        }

    def _build_summary(
        self,
        market: dict[str, Any],
        sectors: list[dict[str, Any]],
        queue: list[dict[str, Any]],
        risks: list[dict[str, Any]],
    ) -> str:
        sector_names = " / ".join(str(item.get("name")) for item in sectors[:3] if item.get("name")) or "No clear sector"
        return (
            f"Market score {market.get('emotion_score')} ({market.get('emotion_label')}). "
            f"Main sectors: {sector_names}. "
            f"Research queue has {len(queue)} names; {len(risks)} need risk-first review. "
            "Next: review sector leaders before individual stocks."
        )

    def _build_risk_alert(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": item.get("code"),
            "code": item.get("code"),
            "name": item.get("name"),
            "risk_score": item.get("risk_score"),
            "summary": item.get("candidate_reason") or item.get("risk_signal") or "Risk needs review.",
            "signals": self.risk_engine.signals(item),
        }

    def _enrich_candidate(
        self,
        item: dict[str, Any],
        market: dict[str, Any],
        sectors: list[dict[str, Any]],
        heat_by_name: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        heat_map = heat_by_name or {sector.get("name"): sector.get("heat_score") for sector in sectors}
        context = {
            "market_score": market.get("emotion_score"),
            "heat_score": heat_map.get(item.get("industry")),
        }
        score = self.scoring_engine.explain_score(item, context)
        action = self.recommendation_engine.next_action(item)
        return {
            **item,
            "research_score": score["totalScore"],
            "score_details": score,
            "risk_level": self.risk_engine.level(item.get("risk_score")),
            "risk_signals": self.risk_engine.signals(item),
            "next_action": action,
            "next_action_reason": self.recommendation_engine.explain(action),
        }
