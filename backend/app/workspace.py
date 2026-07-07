from __future__ import annotations

from datetime import datetime
from typing import Any

from .radar import build_market_radar


def build_workspace() -> dict[str, Any]:
    radar = build_market_radar()
    sectors = [build_hot_sector(item, radar) for item in radar.get("sectors", [])]
    queue = build_research_queue(radar)
    risks = [build_risk_alert(item) for item in queue if (item.get("risk_score") or 0) >= 70][:6]
    return {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "marketPulse": radar.get("market", {}),
        "dailyBrief": build_daily_brief(radar, sectors, queue),
        "researchQueue": queue,
        "hotSectors": sectors,
        "watchlist": [],
        "riskAlerts": risks,
        "raw": radar,
    }


def build_workspace_v1(module: str | None = None) -> dict[str, Any]:
    workspace = build_workspace()
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


def list_watchlist(
    page: int = 1,
    page_size: int = 20,
    q: str = "",
    risk: str = "",
    sort: str = "score",
) -> dict[str, Any]:
    rows = []
    for row in build_research_queue(build_market_radar()):
        risk_level = _risk_level(row.get("risk_score"))
        if q and q.lower() not in str(row.get("name", "")).lower() and q not in str(row.get("code", "")):
            continue
        if risk and risk.lower() != risk_level.lower():
            continue
        rows.append(
            {
                "id": row.get("code"),
                "stockCode": row.get("code"),
                "name": row.get("name"),
                "score": row.get("overall_score"),
                "riskLevel": risk_level,
                "nextAction": _next_action(row),
                "lastAnalysis": datetime.now().isoformat(timespec="seconds"),
                "changeSummary": row.get("candidate_reason"),
            }
        )
    key_map = {"score": "score", "risk": "riskLevel", "code": "stockCode"}
    rows = sorted(rows, key=lambda item: item.get(key_map.get(sort, "score")) or 0, reverse=sort != "code")
    start = max(0, page - 1) * page_size
    return {"items": rows[start : start + page_size], "page": page, "pageSize": page_size, "total": len(rows)}


def add_watchlist_item(payload: dict[str, Any]) -> dict[str, Any]:
    code = str(payload.get("stockCode") or payload.get("code") or "").strip()
    item = next((row for row in build_research_queue(build_market_radar()) if str(row.get("code")) == code), None)
    if not item:
        item = {"code": code, "name": payload.get("name") or code, "overall_score": None, "risk_score": None}
    return {
        "ok": True,
        "item": {
            "id": item.get("code"),
            "stockCode": item.get("code"),
            "name": item.get("name"),
            "score": item.get("overall_score"),
            "riskLevel": _risk_level(item.get("risk_score")),
            "nextAction": _next_action(item),
        },
    }


def queue_action(item_id: str, action: str) -> dict[str, Any]:
    allowed = {"completed", "archived", "researching", "pending"}
    status = action if action in allowed else "pending"
    return {"ok": True, "id": item_id, "status": status, "updatedAt": datetime.now().isoformat(timespec="seconds")}


def telemetry_event(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "requestId": f"tlm-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "event": payload.get("event"),
        "module": payload.get("module"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def build_hot_sector(item: dict[str, Any], radar: dict[str, Any]) -> dict[str, Any]:
    members = [
        row
        for row in radar.get("candidates", [])
        if row.get("industry") == item.get("name") or item.get("name") in str(row.get("candidate_reason", ""))
    ]
    leaders = sorted(members, key=lambda row: row.get("overall_score") or 0, reverse=True)[:5]
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


def build_research_queue(radar: dict[str, Any]) -> list[dict[str, Any]]:
    rows = radar.get("candidates", [])
    return sorted(
        rows,
        key=lambda row: (
            row.get("risk_score") or 0,
            row.get("buy_point_score") or 0,
            row.get("overall_score") or 0,
        ),
        reverse=True,
    )[:10]


def build_daily_brief(radar: dict[str, Any], sectors: list[dict[str, Any]], queue: list[dict[str, Any]]) -> str:
    market = radar.get("market", {})
    summary = radar.get("summary", {})
    sector_names = " / ".join(str(item.get("name")) for item in sectors[:3] if item.get("name")) or "No clear sector"
    risk_count = summary.get("risk_count") or 0
    return (
        f"Market score {market.get('emotion_score')} ({market.get('emotion_label')}). "
        f"Main sectors: {sector_names}. "
        f"Research queue has {len(queue)} names; {risk_count} need risk-first review. "
        f"Next: {summary.get('suggestion') or 'review sector leaders before individual stocks'}"
    )


def build_risk_alert(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("code"),
        "code": item.get("code"),
        "name": item.get("name"),
        "risk_score": item.get("risk_score"),
        "summary": item.get("candidate_reason") or item.get("risk_signal") or "Risk needs review.",
    }


def _risk_level(score: Any) -> str:
    if score is None:
        return "Medium"
    if score >= 70:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def _next_action(item: dict[str, Any]) -> str:
    if (item.get("risk_score") or 0) >= 70:
        return "wait"
    if (item.get("buy_point_score") or 0) >= 65:
        return "research"
    return "observe"


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
