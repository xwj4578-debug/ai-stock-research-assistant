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
