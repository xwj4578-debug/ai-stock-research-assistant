from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class StockListing:
    code: str
    name: str
    price: float | None
    change_pct: float | None
    market_cap: float | None
    pe: float | None
    pb: float | None


_CACHE: dict[str, Any] = {"loaded_at": 0.0, "rows": []}
_TTL_SECONDS = 60 * 60


def _clean(value: Any) -> float | None:
    if value in (None, "-", ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _market_cap_yi(value: Any) -> float | None:
    raw = _clean(value)
    if raw is None:
        return None
    return round(raw / 100_000_000, 1)


def _normalize(text: str) -> str:
    return (
        text.strip()
        .replace(" ", "")
        .replace("\u3000", "")
        .replace("Ａ", "A")
        .replace("Ｂ", "B")
        .lower()
    )


def _fetch_page(page: int, size: int = 100) -> tuple[int, list[StockListing]]:
    params = urlencode(
        {
            "pn": page,
            "pz": size,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f12,f14,f2,f3,f20,f9,f23",
        }
    )
    request = Request(
        f"https://push2.eastmoney.com/api/qt/clist/get?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urlopen(request, timeout=4) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data") or {}
    rows = [
        StockListing(
            code=str(item.get("f12") or ""),
            name=str(item.get("f14") or "").replace(" ", ""),
            price=_clean(item.get("f2")),
            change_pct=_clean(item.get("f3")),
            market_cap=_market_cap_yi(item.get("f20")),
            pe=_clean(item.get("f9")),
            pb=_clean(item.get("f23")),
        )
        for item in data.get("diff") or []
        if item.get("f12") and item.get("f14")
    ]
    return int(data.get("total") or 0), rows


def search_a_share_suggest(query: str, limit: int = 10) -> list[StockListing]:
    normalized = _normalize(query)
    if not normalized:
        return []
    params = urlencode(
        {
            "input": query,
            "type": 14,
            "token": "D43BF722C8E33BDC906FB84D85E326E8",
            "count": limit,
        }
    )
    request = Request(
        f"https://searchapi.eastmoney.com/api/suggest/get?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []
    rows = []
    for item in ((payload.get("QuotationCodeTable") or {}).get("Data") or []):
        if item.get("Classify") != "AStock":
            continue
        code = str(item.get("Code") or "")
        name = str(item.get("Name") or "").replace(" ", "")
        if not code or not name:
            continue
        rows.append(StockListing(code=code, name=name, price=None, change_pct=None, market_cap=None, pe=None, pb=None))
    return rows


def all_a_share_listings(force_refresh: bool = False) -> list[StockListing]:
    now = time.time()
    if not force_refresh and _CACHE["rows"] and now - _CACHE["loaded_at"] < _TTL_SECONDS:
        return _CACHE["rows"]

    first_total, first_rows = _fetch_page(1)
    size = 100
    total_pages = max(1, (first_total + size - 1) // size)
    rows = list(first_rows)
    for page in range(2, total_pages + 1):
        try:
            _, page_rows = _fetch_page(page, size=size)
        except Exception:
            continue
        rows.extend(page_rows)

    _CACHE["loaded_at"] = now
    _CACHE["rows"] = rows
    return rows


def find_a_share(query: str) -> StockListing | None:
    normalized = _normalize(query)
    if not normalized:
        return None
    suggested = search_a_share_suggest(query, limit=20)
    def enrich(row: StockListing) -> StockListing:
        try:
            for full in all_a_share_listings():
                if full.code == row.code:
                    return full
        except Exception:
            return row
        return row

    for row in suggested:
        if normalized == row.code.lower() or normalized == _normalize(row.name):
            return enrich(row)
    if suggested:
        return enrich(suggested[0])
    try:
        rows = all_a_share_listings()
    except Exception:
        return None

    for row in rows:
        if normalized == row.code.lower() or normalized == _normalize(row.name):
            return row
    for row in rows:
        if normalized in row.code.lower() or normalized in _normalize(row.name):
            return row
    return None


def search_a_shares(query: str, limit: int = 20) -> list[StockListing]:
    normalized = _normalize(query)
    if not normalized:
        return []
    suggested = search_a_share_suggest(query, limit=limit)
    if suggested:
        return suggested[:limit]
    try:
        rows = all_a_share_listings()
    except Exception:
        return []

    exact = [row for row in rows if normalized == row.code.lower() or normalized == _normalize(row.name)]
    fuzzy = [row for row in rows if row not in exact and (normalized in row.code.lower() or normalized in _normalize(row.name))]
    return (exact + fuzzy)[:limit]


def find_a_share_in_text(text: str) -> StockListing | None:
    normalized = _normalize(text)
    if not normalized:
        return None
    try:
        rows = all_a_share_listings()
    except Exception:
        return None
    code_matches = [row for row in rows if row.code and row.code in normalized]
    if code_matches:
        return sorted(code_matches, key=lambda row: len(row.code), reverse=True)[0]
    name_matches = [row for row in rows if _normalize(row.name) and _normalize(row.name) in normalized]
    if not name_matches:
        return None
    return sorted(name_matches, key=lambda row: len(_normalize(row.name)), reverse=True)[0]
