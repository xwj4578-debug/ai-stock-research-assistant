from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from .data import FinancialYear


def _num(value: Any) -> float:
    if value in (None, "-", ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _yi(value: Any) -> float:
    return round(_num(value) / 100_000_000, 2)


def _percent(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def fetch_financial_years(code: str, limit: int = 5) -> list[FinancialYear]:
    if not code.isdigit() or len(code) != 6:
        return []
    filter_expr = quote(f'(SECURITY_CODE="{code}")', safe="()=")
    url = (
        "https://datacenter-web.eastmoney.com/api/data/v1/get"
        "?reportName=RPT_F10_FINANCE_MAINFINADATA"
        "&columns=ALL"
        f"&filter={filter_expr}"
        "&pageNumber=1&pageSize=40"
        "&sortColumns=REPORT_DATE&sortTypes=-1"
    )
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    rows = (payload.get("result") or {}).get("data") or []
    annual_rows = [
        row
        for row in rows
        if str(row.get("REPORT_DATE", ""))[5:10] == "12-31" or str(row.get("REPORT_TYPE", "")) == "年报"
    ]
    annual_rows = sorted(annual_rows, key=lambda row: str(row.get("REPORT_DATE", "")))[-limit:]
    result = []
    for row in annual_rows:
        revenue = _yi(row.get("TOTALOPERATEREVE"))
        profit = _yi(row.get("PARENTNETPROFIT"))
        result.append(
            FinancialYear(
                year=int(str(row.get("REPORT_YEAR") or str(row.get("REPORT_DATE", ""))[:4] or 0)),
                revenue=revenue,
                net_profit=profit,
                gross_margin=round(_num(row.get("XSMLL")), 2),
                net_margin=_percent(profit, revenue),
                roe=round(_num(row.get("ROEJQ")), 2),
                roa=0.0,
                eps=round(_num(row.get("EPSJB")), 2),
                free_cash_flow=_yi(row.get("NETCASH_OPERATE_PK")),
                debt_ratio=round(_num(row.get("ZCFZL")), 2),
                rd_expense=0.0,
                cash=0.0,
            )
        )
    return [item for item in result if item.year]
