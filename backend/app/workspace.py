from __future__ import annotations

from typing import Any

from .application import workspace_service


def build_workspace() -> dict[str, Any]:
    return workspace_service.build_workspace()


def build_workspace_v1(module: str | None = None) -> dict[str, Any]:
    return workspace_service.build_workspace_v1(module=module)


def list_watchlist(
    page: int = 1,
    page_size: int = 20,
    q: str = "",
    risk: str = "",
    sort: str = "score",
) -> dict[str, Any]:
    return workspace_service.list_watchlist(page=page, page_size=page_size, q=q, risk=risk, sort=sort)


def add_watchlist_item(payload: dict[str, Any]) -> dict[str, Any]:
    return workspace_service.add_watchlist_item(payload)


def queue_action(item_id: str, action: str) -> dict[str, Any]:
    return workspace_service.queue_action(item_id=item_id, action=action)


def telemetry_event(payload: dict[str, Any]) -> dict[str, Any]:
    return workspace_service.telemetry_event(payload)


def copilot_metadata() -> dict[str, Any]:
    return {
        "role": "active research partner",
        "capabilities": [
            "summarize_market",
            "compare_stocks",
            "analyze_sector",
            "interpret_announcement",
            "explain_scores",
            "recommend_next_tasks",
        ],
        "suggestedPrompts": [
            "Summarize today's market in 5 bullets.",
            "Which sector should I research first?",
            "Explain why this stock has a high risk score.",
        ],
    }


def copilot_reply(payload: dict[str, Any]) -> dict[str, Any]:
    workspace = build_workspace()
    sectors = workspace["hotSectors"]
    top = sectors[0] if sectors else {}
    question = str(payload.get("message") or payload.get("intent") or "recommend_next_tasks")
    return {
        "question": question,
        "answer": {
            "reason": top.get("ai_summary") or workspace["dailyBrief"],
            "leader": top.get("leader") or "Pending",
            "trend_core": top.get("trend_core") or "Pending",
            "risk": "Risk score is priority; a higher risk score means more dangerous, not more attractive.",
            "next_watch_points": [
                "Check whether sector heat stays above 70.",
                "Review the leader and trend core before adding new names.",
                "If risk alerts increase, stop expanding the watchlist.",
            ],
        },
    }
