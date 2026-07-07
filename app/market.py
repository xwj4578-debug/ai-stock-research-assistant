from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class MarketTarget:
    name: str
    secid: str
    kind: str


INDEX_TARGETS = {
    "上证指数": MarketTarget("上证指数", "1.000001", "index"),
    "深证成指": MarketTarget("深证成指", "0.399001", "index"),
    "创业板指": MarketTarget("创业板指", "0.399006", "index"),
    "科创50": MarketTarget("科创50", "1.000688", "index"),
}

SECTOR_ALIASES = {
    "半导体": MarketTarget("半导体", "90.BK1036", "sector"),
    "芯片": MarketTarget("半导体", "90.BK1036", "sector"),
    "软件": MarketTarget("软件开发", "90.BK0737", "sector"),
    "软件开发": MarketTarget("软件开发", "90.BK0737", "sector"),
    "通信设备": MarketTarget("通信设备", "90.BK0448", "sector"),
    "通信": MarketTarget("通信设备", "90.BK0448", "sector"),
    "元件": MarketTarget("元件", "90.BK0459", "sector"),
    "消费电子": MarketTarget("消费电子", "90.BK1037", "sector"),
    "计算机设备": MarketTarget("计算机设备", "90.BK0735", "sector"),
    "证券": MarketTarget("证券Ⅱ", "90.BK0473", "sector"),
    "银行": MarketTarget("银行Ⅱ", "90.BK0475", "sector"),
}

_BOARD_CACHE: dict[str, Any] = {"loaded_at": 0.0, "rows": []}
_TTL_SECONDS = 60 * 30


def _get_json(url: str, timeout: float = 6) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _num(value: Any, scale: float = 1) -> float | None:
    if value in (None, "-", ""):
        return None
    try:
        return round(float(value) / scale, 2)
    except (TypeError, ValueError):
        return None


def _normalize(text: str) -> str:
    return text.strip().replace(" ", "").replace("Ａ", "A").lower()


def fetch_quote(secid: str) -> dict[str, Any] | None:
    params = urlencode({"secid": secid, "fields": "f43,f57,f58,f170,f47,f48"})
    try:
        payload = _get_json(f"https://push2.eastmoney.com/api/qt/stock/get?{params}", timeout=4)
    except Exception:
        return None
    data = payload.get("data") or {}
    if not data:
        return None
    return {
        "code": data.get("f57"),
        "name": data.get("f58"),
        "price": _num(data.get("f43"), 100),
        "change_pct": _num(data.get("f170"), 100),
        "volume": _num(data.get("f47")),
        "amount": _num(data.get("f48")),
    }


def fetch_klines(secid: str, limit: int = 30) -> list[dict[str, Any]]:
    params = urlencode(
        {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": 101,
            "fqt": 1,
            "beg": 20200101,
            "end": 20500101,
            "lmt": limit,
        }
    )
    try:
        payload = _get_json(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?{params}", timeout=6)
    except Exception:
        return []
    rows = (payload.get("data") or {}).get("klines") or []
    result = []
    for row in rows:
        parts = str(row).split(",")
        if len(parts) < 11:
            continue
        result.append(
            {
                "date": parts[0],
                "open": _num(parts[1]),
                "close": _num(parts[2]),
                "high": _num(parts[3]),
                "low": _num(parts[4]),
                "volume": _num(parts[5]) or 0,
                "amount": _num(parts[6]) or 0,
                "amplitude": _num(parts[7]),
                "change_pct": _num(parts[8]),
                "change": _num(parts[9]),
                "turnover": _num(parts[10]),
            }
        )
    return result


def fetch_board_list(force_refresh: bool = False) -> list[dict[str, Any]]:
    now = time.time()
    if not force_refresh and _BOARD_CACHE["rows"] and now - _BOARD_CACHE["loaded_at"] < _TTL_SECONDS:
        return _BOARD_CACHE["rows"]
    rows = []
    page = 1
    while True:
        params = (
            f"pn={page}&pz=100&po=1&np=1&fltt=2&invt=2"
            "&fs=m:90+t:2"
            "&fields=f12,f14,f3"
        )
        try:
            payload = _get_json(f"https://push2.eastmoney.com/api/qt/clist/get?{params}", timeout=6)
        except Exception:
            break
        data = payload.get("data") or {}
        diff = data.get("diff") or []
        rows.extend({"code": item.get("f12"), "name": item.get("f14"), "change_pct": item.get("f3")} for item in diff)
        total = int(data.get("total") or len(rows))
        if len(rows) >= total or not diff:
            break
        page += 1
    _BOARD_CACHE["rows"] = rows
    _BOARD_CACHE["loaded_at"] = now
    return rows


def resolve_market_target(query: str) -> MarketTarget:
    normalized = _normalize(query)
    for name, target in INDEX_TARGETS.items():
        if normalized in _normalize(name) or _normalize(name) in normalized:
            return target
    if normalized in {"大盘", "市场", "a股", "上证"}:
        return INDEX_TARGETS["上证指数"]
    if normalized in {"科技", "科技股", "科技板块"}:
        return INDEX_TARGETS["科创50"]
    for name, target in SECTOR_ALIASES.items():
        if normalized in _normalize(name) or _normalize(name) in normalized:
            return target
    for row in fetch_board_list():
        if not row.get("name") or not row.get("code"):
            continue
        if normalized in _normalize(row["name"]) or _normalize(row["name"]) in normalized:
            return MarketTarget(row["name"], f"90.{row['code']}", "sector")
    return INDEX_TARGETS["科创50"]


def analyze_target(target: MarketTarget) -> dict[str, Any]:
    quote = fetch_quote(target.secid) or {"name": target.name, "change_pct": None}
    klines = fetch_klines(target.secid)
    latest = klines[-1] if klines else {}
    if not latest:
        return {
            "target": {"name": quote.get("name") or target.name, "secid": target.secid, "kind": target.kind},
            "quote": quote,
            "latest": {},
            "ma5": None,
            "ma10": None,
            "amount_ratio": None,
            "state": "数据源暂不可用",
            "risk_score": 1,
            "signals": ["暂未取得指数/板块K线，不能生成盘面研判。"],
            "scenarios": [
                "恢复行情接口后，系统会重新计算5日/10日均线、涨跌幅和量能变化。",
                "没有实时K线时，不输出退潮、修复或主升判断，避免误导用户。",
            ],
            "conclusion": f"{quote.get('name') or target.name}暂未取得足够行情数据。本模块只做盘面风险研判，不做确定性涨跌预测。",
        }
    if quote.get("change_pct") is None and latest:
        quote = {
            **quote,
            "name": quote.get("name") or target.name,
            "price": latest.get("close"),
            "change_pct": latest.get("change_pct"),
            "amount": latest.get("amount"),
        }
    closes = [row["close"] for row in klines if row.get("close") is not None]
    amounts = [row["amount"] for row in klines if row.get("amount") is not None]
    ma5 = round(sum(closes[-5:]) / 5, 2) if len(closes) >= 5 else None
    ma10 = round(sum(closes[-10:]) / 10, 2) if len(closes) >= 10 else None
    avg_amount5 = sum(amounts[-6:-1]) / 5 if len(amounts) >= 6 else None
    amount_ratio = round(latest.get("amount", 0) / avg_amount5, 2) if avg_amount5 else None
    close = latest.get("close")
    pct = latest.get("change_pct")
    below_ma5 = bool(close is not None and ma5 is not None and close < ma5)
    below_ma10 = bool(close is not None and ma10 is not None and close < ma10)
    heavy_down = bool(pct is not None and pct <= -2 and amount_ratio is not None and amount_ratio >= 1.1)
    heavy_up = bool(pct is not None and pct >= 2 and amount_ratio is not None and amount_ratio >= 1.1)

    risk_score = 0
    signals = []
    if below_ma5:
        risk_score += 1
        signals.append("收盘价跌破5日均线")
    if below_ma10:
        risk_score += 1
        signals.append("收盘价跌破10日均线")
    if heavy_down:
        risk_score += 2
        signals.append(f"放量下跌，成交额约为5日均量的{amount_ratio}倍")
    if pct is not None and pct <= -4:
        risk_score += 1
        signals.append("单日跌幅较大")
    if heavy_up:
        signals.append(f"放量上涨，成交额约为5日均量的{amount_ratio}倍")

    if risk_score >= 4:
        state = "恐慌/退潮信号强"
    elif risk_score >= 2:
        state = "退潮信号增强"
    elif risk_score == 1:
        state = "分歧"
    elif heavy_up:
        state = "修复/主升"
    else:
        state = "中性震荡"

    if not signals:
        signals.append("未触发关键风险信号")

    scenarios = [
        "若后续继续放量下跌且无法收回5日均线，退潮信号进一步增强。",
        "若缩量企稳并重新站上5日均线，说明更可能是强势板块内部消化。",
        "若龙头股先于板块修复，板块风险偏好可能回升；若龙头补跌，需防止风险扩散。",
    ]
    return {
        "target": {"name": quote.get("name") or target.name, "secid": target.secid, "kind": target.kind},
        "quote": quote,
        "latest": latest,
        "ma5": ma5,
        "ma10": ma10,
        "amount_ratio": amount_ratio,
        "state": state,
        "risk_score": risk_score,
        "signals": signals,
        "scenarios": scenarios,
        "conclusion": f"{quote.get('name') or target.name}当前状态为{state}。这不是涨跌预测，而是基于均线、涨跌幅和成交额的盘面风险研判。",
    }


def market_overview() -> dict[str, Any]:
    targets = [INDEX_TARGETS["上证指数"], INDEX_TARGETS["深证成指"], INDEX_TARGETS["创业板指"], INDEX_TARGETS["科创50"]]
    items = [analyze_target(target) for target in targets]
    avg_risk = round(sum(item["risk_score"] for item in items) / len(items), 2)
    if avg_risk >= 3:
        state = "市场风险偏高"
    elif avg_risk >= 1.5:
        state = "市场分歧加大"
    else:
        state = "市场整体中性"
    return {"state": state, "avg_risk": avg_risk, "items": items}
