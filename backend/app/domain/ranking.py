from __future__ import annotations

from typing import Any

from .config_loader import load_domain_config


def rank_research_queue(rows: list[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    config = load_domain_config("ranking.yaml")["research_queue"]
    fields = config["fields"]
    final_limit = limit or config["limit"]
    return sorted(
        rows,
        key=lambda row: _weighted_score(row, fields),
        reverse=True,
    )[:final_limit]


def rank_sector_leaders(rows: list[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    config = load_domain_config("ranking.yaml")["sector_leaders"]
    final_limit = limit or config["limit"]
    return sorted(rows, key=lambda row: _weighted_score(row, config["fields"]), reverse=True)[:final_limit]


def _weighted_score(row: dict[str, Any], fields: dict[str, float]) -> float:
    total = 0.0
    for field, weight in fields.items():
        if field == "watchlist_boost":
            value = 100 if row.get("in_watchlist") else 0
        else:
            value = row.get(field) or 0
        total += float(value) * float(weight)
    return total
