from __future__ import annotations

from datetime import datetime
from typing import Any

from ..domain import ResearchEngine, next_action, risk_level
from ..providers import EastMoneyProvider, MockMarketProvider
from ..repository import MarketRepository


class WorkspaceService:
    def __init__(self, engine: ResearchEngine | None = None) -> None:
        repository = MarketRepository(provider=EastMoneyProvider(), fallback_provider=MockMarketProvider())
        self.engine = engine or ResearchEngine(repository)

    def build_workspace(self) -> dict[str, Any]:
        return self.engine.build_workspace_model()

    def build_workspace_v1(self, module: str | None = None) -> dict[str, Any]:
        workspace = self.build_workspace()
        response = {
            "requestId": f"ws-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "state": "Ready",
            "generatedAt": workspace["generatedAt"],
            "marketPulse": workspace["marketPulse"],
            "dailyBrief": {"summary": workspace["dailyBrief"], "status": "Ready"},
            "researchQueue": workspace["researchQueue"],
            "hotSectors": workspace["hotSectors"],
            "watchlist": workspace["watchlist"],
            "riskAlerts": workspace["riskAlerts"],
            "moduleStates": {
                "marketPulse": "Ready",
                "dailyBrief": "Ready",
                "researchQueue": "Ready",
                "hotSectors": "Ready",
                "watchlist": "Empty",
                "riskAlerts": "Ready" if workspace["riskAlerts"] else "Empty",
            },
            "performance": {"cache": "memory", "targetMs": 500},
            "dataEngine": {
                "application": "WorkspaceService",
                "domain": "ResearchEngine",
                "repository": "MarketRepository",
                "provider": "EastMoneyProvider",
                "fallbackProvider": "MockMarketProvider",
            },
            "raw": workspace["raw"],
        }
        if module:
            allowed = {"marketPulse", "dailyBrief", "researchQueue", "hotSectors", "watchlist", "riskAlerts"}
            if module in allowed:
                return {
                    "requestId": response["requestId"],
                    "state": response["moduleStates"].get(module, "Ready"),
                    module: response[module],
                    "generatedAt": response["generatedAt"],
                }
        return response

    def get_market_overview(self) -> dict[str, Any]:
        market = self.build_workspace()["marketPulse"]
        stats = market.get("stats") or {}
        return {
            "score": market.get("emotion_score") or 0,
            "status": market.get("emotion_label") or "待确认",
            "turnover": f"{stats.get('amount_yi') or 0} 亿",
            "upCount": stats.get("rising_count") or 0,
            "downCount": stats.get("falling_count") or 0,
            "limitUp": stats.get("limit_up_count") or 0,
            "limitDown": stats.get("limit_down_count") or 0,
            "brokenRate": f"{stats.get('failed_limit_rate') or 0}%",
            "leadingHeight": "数据待接入",
            "summary": market.get("advice") or "市场状态待确认。",
            "source": "backend",
        }

    def get_hot_sectors(self) -> list[dict[str, Any]]:
        return [
            {
                "name": item.get("name") or "板块待确认",
                "change": _signed_percent(item.get("change_pct")),
                "score": item.get("heat_score") or 0,
                "leader": item.get("leader") or "待确认",
                "reason": item.get("ai_summary") or "板块逻辑待确认。",
                "trendCore": item.get("trend_core") or item.get("leader") or "待确认",
                "reboundStock": (item.get("members") or [{}])[-1].get("name") if item.get("members") else "待确认",
                "risk": "热度过高时注意分化，不追后排。",
                "relatedStocks": [row.get("name") for row in (item.get("members") or [])[:6] if row.get("name")],
            }
            for item in self.build_workspace()["hotSectors"]
        ]

    def get_research_queue(self) -> list[dict[str, Any]]:
        return [
            {
                "code": item.get("code"),
                "name": item.get("name"),
                "score": item.get("research_score") or item.get("overall_score") or 0,
                "status": item.get("status") or "待研究",
                "reason": item.get("candidate_reason") or item.get("summary") or "研究理由待确认。",
                "sector": item.get("industry"),
                "conclusion": item.get("summary") or item.get("candidate_reason"),
                "riseLogic": item.get("buy_signal") or item.get("capital_state") or "资金和板块逻辑待确认。",
                "riskTip": item.get("risk_signal") or "风险待确认。",
                "nextStep": item.get("next_action_reason") or item.get("watch_reason"),
                "scoreDetails": item.get("score_details"),
            }
            for item in self.build_workspace()["researchQueue"]
        ]

    def get_research_score(self, code: str) -> dict[str, Any]:
        item = next((row for row in self.build_workspace()["researchQueue"] if str(row.get("code")) == code), None)
        if not item:
            return {"code": code, "scoreDetails": None, "error": "not_found"}
        return {
            "code": code,
            "name": item.get("name"),
            "score": item.get("research_score") or item.get("overall_score"),
            "scoreDetails": item.get("score_details"),
        }

    def list_watchlist(self, page: int = 1, page_size: int = 20, q: str = "", risk: str = "", sort: str = "score") -> dict[str, Any]:
        rows = []
        for row in self.engine.list_watchlist_candidates():
            if q and q.lower() not in str(row.get("name", "")).lower() and q not in str(row.get("stockCode", "")):
                continue
            if risk and risk.lower() != str(row.get("riskLevel", "")).lower():
                continue
            rows.append(row)
        key_map = {"score": "score", "risk": "riskLevel", "code": "stockCode"}
        rows = sorted(rows, key=lambda item: item.get(key_map.get(sort, "score")) or 0, reverse=sort != "code")
        start = max(0, page - 1) * page_size
        return {"items": rows[start : start + page_size], "page": page, "pageSize": page_size, "total": len(rows)}

    def add_watchlist_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        code = str(payload.get("stockCode") or payload.get("code") or "").strip()
        item = self.engine.find_candidate(code) or {"code": code, "name": payload.get("name") or code, "overall_score": None, "risk_score": None}
        return {
            "ok": True,
            "item": {
                "id": item.get("code"),
                "stockCode": item.get("code"),
                "name": item.get("name"),
                "score": item.get("overall_score"),
                "riskLevel": risk_level(item.get("risk_score")),
                "nextAction": next_action(item),
            },
        }

    def queue_action(self, item_id: str, action: str) -> dict[str, Any]:
        allowed = {"completed", "archived", "researching", "pending"}
        status = action if action in allowed else "pending"
        return {"ok": True, "id": item_id, "status": status, "updatedAt": datetime.now().isoformat(timespec="seconds")}

    def telemetry_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "requestId": f"tlm-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "event": payload.get("event"),
            "module": payload.get("module"),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }


workspace_service = WorkspaceService()


def _signed_percent(value: Any) -> str:
    if value is None:
        return "0%"
    numeric = float(value)
    prefix = "+" if numeric > 0 else ""
    return f"{prefix}{numeric}%"
