from __future__ import annotations

from fastapi import APIRouter, Query

from ..application import workspace_service

router = APIRouter(prefix="/api/v1", tags=["workspace"])


@router.get("/workspace")
def workspace_v1(module: str | None = None) -> dict:
    return workspace_service.build_workspace_v1(module=module)


@router.get("/market/overview")
def market_overview() -> dict:
    return workspace_service.get_market_overview()


@router.get("/market/sectors")
def market_sectors() -> list[dict]:
    return workspace_service.get_hot_sectors()


@router.get("/research/queue")
def research_queue() -> list[dict]:
    return workspace_service.get_research_queue()


@router.get("/research/score/{code}")
def research_score(code: str) -> dict:
    return workspace_service.get_research_score(code)


@router.get("/watchlist")
def watchlist(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str = "",
    risk: str = "",
    sort: str = Query("score", pattern="^(score|risk|code)$"),
) -> dict:
    return workspace_service.list_watchlist(page=page, page_size=page_size, q=q, risk=risk, sort=sort)


@router.post("/watchlist")
def add_watchlist(payload: dict) -> dict:
    return workspace_service.add_watchlist_item(payload)


@router.delete("/watchlist/{item_id}")
def delete_watchlist(item_id: str) -> dict:
    return {"ok": True, "deleted": item_id}


@router.post("/research-queue/{item_id}/{action}")
def research_queue_action(item_id: str, action: str) -> dict:
    return workspace_service.queue_action(item_id=item_id, action=action)


@router.post("/telemetry")
def telemetry(payload: dict) -> dict:
    return workspace_service.telemetry_event(payload)
