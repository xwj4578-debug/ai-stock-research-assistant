from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.request import Request, urlopen

from .company_profile import fetch_company_profile
from .financials import fetch_financial_years
from .live_market import fetch_live_quote
from .research import fetch_announcements
from .stock_universe import StockListing, find_a_share, search_a_shares


_CACHE: dict[str, tuple[float, Any]] = {}
_TZ = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class Kline:
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    amount: float | None = None
    amplitude: float | None = None
    change_pct: float | None = None
    turnover_rate: float | None = None


def _now() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _market(code: str) -> str:
    return "SH" if code.startswith(("6", "9")) else "SZ"


def _symbol(code: str) -> str:
    return ("sh" if _market(code) == "SH" else "sz") + code


def _secid(code: str) -> str:
    return f"{1 if _market(code) == 'SH' else 0}.{code}"


def _num(value: Any) -> float | None:
    if value in (None, "", "-", "--"):
        return None
    try:
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, 2)
    except (TypeError, ValueError):
        return None


def _cached(key: str, ttl: int, loader):
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1]
    value = loader()
    _CACHE[key] = (now, value)
    return value


def _read_text(url: str, timeout: float = 8, referer: str = "https://quote.eastmoney.com/") -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Referer": referer,
    }
    try:
        with urlopen(Request(url, headers=headers), timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception:
        pass

    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        return None
    try:
        completed = subprocess.run(
            [curl, "-L", "-s", "--max-time", str(max(3, int(timeout))), "-H", "User-Agent: Mozilla/5.0", "-H", f"Referer: {referer}", url],
            check=False,
            capture_output=True,
            text=False,
            timeout=timeout + 2,
        )
        if completed.stdout.strip():
            return completed.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return None
    return None


def _read_json(url: str, timeout: float = 8, referer: str = "https://quote.eastmoney.com/") -> dict[str, Any] | list[Any] | None:
    text = _read_text(url, timeout=timeout, referer=referer)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None


def search_stock(keyword: str, limit: int = 20) -> list[dict[str, Any]]:
    rows = search_a_shares(keyword, limit=limit)
    return [{"code": row.code, "name": row.name, "market": _market(row.code), "type": "stock"} for row in rows]


def resolve_stock(keyword_or_code: str) -> StockListing | None:
    return find_a_share((keyword_or_code or "").strip())


def _kline_from_tencent(code: str, days: int) -> tuple[list[Kline], dict[str, Any]]:
    symbol = _symbol(code)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,{days},qfq"
    payload = _read_json(url, timeout=10, referer="https://gu.qq.com/")
    data = ((payload or {}).get("data") or {}).get(symbol) if isinstance(payload, dict) else None
    rows = (data or {}).get("qfqday") or (data or {}).get("day") or []
    result: list[Kline] = []
    previous_close: float | None = None
    for row in rows[-days:]:
        if len(row) < 6:
            continue
        open_, close, high, low, volume = (_num(row[1]), _num(row[2]), _num(row[3]), _num(row[4]), _num(row[5]))
        if None in (open_, close, high, low, volume):
            continue
        amplitude = round((high - low) / previous_close * 100, 2) if previous_close else None
        change_pct = round((close / previous_close - 1) * 100, 2) if previous_close else None
        amount = None
        turnover_rate = None
        qt = ((data or {}).get("qt") or {}).get(symbol) or []
        if row == rows[-1] and len(qt) > 38:
            amount = _num(qt[37])
            amount = amount * 10_000 if amount is not None else None
            turnover_rate = _num(qt[38])
        result.append(Kline(str(row[0]), open_, close, high, low, volume, amount, amplitude, change_pct, turnover_rate))
        previous_close = close
    return result, {"source": "腾讯证券公开K线接口"}


def _kline_from_eastmoney(code: str, days: int) -> tuple[list[Kline], dict[str, Any]]:
    params = (
        f"secid={_secid(code)}"
        "&fields1=f1,f2,f3,f4,f5,f6"
        "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&klt=101&fqt=1&beg=20200101&end=20500101&lmt={days}"
    )
    payload = _read_json(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?{params}", timeout=10)
    rows = ((payload or {}).get("data") or {}).get("klines") if isinstance(payload, dict) else []
    result: list[Kline] = []
    for row in (rows or [])[-days:]:
        parts = str(row).split(",")
        if len(parts) < 11:
            continue
        values = [_num(item) for item in parts[1:11]]
        if any(item is None for item in values[:6]):
            continue
        result.append(Kline(parts[0], values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[9]))
    return result, {"source": "东方财富公开K线接口"}


def _kline_from_sina(code: str, days: int) -> tuple[list[Kline], dict[str, Any]]:
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={_symbol(code)}&scale=240&ma=no&datalen={days}"
    payload = _read_json(url, timeout=10, referer="https://finance.sina.com.cn/")
    if not isinstance(payload, list):
        return [], {"source": "新浪财经公开K线接口"}
    result: list[Kline] = []
    previous_close: float | None = None
    for row in payload[-days:]:
        open_, close, high, low, volume = (_num(row.get("open")), _num(row.get("close")), _num(row.get("high")), _num(row.get("low")), _num(row.get("volume")))
        if None in (open_, close, high, low, volume):
            continue
        amplitude = round((high - low) / previous_close * 100, 2) if previous_close else None
        change_pct = round((close / previous_close - 1) * 100, 2) if previous_close else None
        result.append(Kline(str(row.get("day")), open_, close, high, low, volume, None, amplitude, change_pct, None))
        previous_close = close
    return result, {"source": "新浪财经公开K线接口"}


def get_daily_kline(code: str, days: int = 250) -> tuple[list[Kline], dict[str, Any]]:
    def load() -> tuple[list[Kline], dict[str, Any]]:
        for loader in (_kline_from_tencent, _kline_from_eastmoney, _kline_from_sina):
            rows, meta = loader(code, days)
            if len(rows) >= min(30, days):
                return rows, meta
        return [], {"source": "公开K线接口", "error": "K线数据暂不可用"}

    return _cached(f"kline:{code}:{days}", 60, load)


def _ma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return round(sum(values[-window:]) / window, 2)


def _pct(start: float | None, end: float | None) -> float | None:
    if not start or end is None:
        return None
    return round((end / start - 1) * 100, 2)


def _money_yi(value: float | None) -> float | None:
    return round(value / 100_000_000, 2) if value is not None else None


def get_quote(code: str, klines: list[Kline]) -> dict[str, Any]:
    latest = klines[-1] if klines else None
    live = fetch_live_quote(code) or {}
    price = live.get("price") or (latest.close if latest else None)
    return {
        "price": price,
        "change_pct": live.get("change_pct") if live.get("change_pct") is not None else (latest.change_pct if latest else None),
        "high": latest.high if latest else None,
        "low": latest.low if latest else None,
        "amount": latest.amount if latest and latest.amount else None,
        "amount_yi": _money_yi(latest.amount if latest else None),
        "turnover_rate": latest.turnover_rate if latest else None,
        "update_time": live.get("updated_at") or (f"{latest.date} 15:00:00" if latest else _now()),
        "source": live.get("source") or "公开行情接口",
    }


def position_metrics(klines: list[Kline]) -> dict[str, Any]:
    closes = [row.close for row in klines]
    latest = klines[-1] if klines else None

    def high_low(days: int):
        part = klines[-days:] if len(klines) >= days else klines
        if not part:
            return None, None
        return max(row.high for row in part), min(row.low for row in part)

    high_20, low_20 = high_low(20)
    high_60, low_60 = high_low(60)
    high_120, low_120 = high_low(120)
    stage = klines[-120:] if len(klines) >= 120 else klines
    stage_high_row = max(stage, key=lambda row: row.high) if stage else None
    price = latest.close if latest else None
    return {
        "high_20d": high_20,
        "low_20d": low_20,
        "high_60d": high_60,
        "low_60d": low_60,
        "high_120d": high_120,
        "low_120d": low_120,
        "stage_high": stage_high_row.high if stage_high_row else None,
        "stage_high_date": stage_high_row.date if stage_high_row else None,
        "drawdown_from_stage_high_pct": _pct(stage_high_row.high if stage_high_row else None, price),
        "ma5": _ma(closes, 5),
        "ma10": _ma(closes, 10),
        "ma20": _ma(closes, 20),
        "ma30": _ma(closes, 30),
        "ma60": _ma(closes, 60),
        "ma120": _ma(closes, 120),
        "distance_ma5_pct": _pct(_ma(closes, 5), price),
        "distance_ma10_pct": _pct(_ma(closes, 10), price),
        "distance_ma20_pct": _pct(_ma(closes, 20), price),
        "distance_ma30_pct": _pct(_ma(closes, 30), price),
        "distance_ma60_pct": _pct(_ma(closes, 60), price),
        "distance_ma120_pct": _pct(_ma(closes, 120), price),
    }


def moving_average_signals(klines: list[Kline], current_price: float | None) -> dict[str, Any]:
    closes = [row.close for row in klines]
    price = current_price or (closes[-1] if closes else None)
    windows = [5, 10, 20, 30, 60, 120]
    items: list[dict[str, Any]] = []
    for window in windows:
        if len(closes) < window or price is None:
            items.append({"name": f"MA{window}", "price": None, "status": "暂无数据", "distance_pct": None, "tip": "K线数量不足"})
            continue
        dynamic_closes = closes[:]
        dynamic_closes[-1] = price
        ma_price = round(sum(dynamic_closes[-window:]) / window, 2)
        distance_pct = _pct(ma_price, price)
        if distance_pct is None:
            status = "暂无数据"
        elif abs(distance_pct) <= 0.5:
            status = "贴近均线"
        elif distance_pct > 0:
            status = "站上均线"
        else:
            status = "跌破均线"
        action = "跌破" if distance_pct is not None and distance_pct >= 0 else "站回"
        items.append(
            {
                "name": f"MA{window}",
                "price": ma_price,
                "status": status,
                "distance_pct": distance_pct,
                "tip": f"{action}{ma_price}元要重新观察",
            }
        )
    valid = [item for item in items if item["price"] is not None]
    above = [item for item in valid if (item.get("distance_pct") or 0) > 0.5]
    below = [item for item in valid if (item.get("distance_pct") or 0) < -0.5]
    ma5 = next((item for item in items if item["name"] == "MA5"), None)
    ma10 = next((item for item in items if item["name"] == "MA10"), None)
    if ma5 and ma10 and ma5.get("distance_pct") is not None and ma10.get("distance_pct") is not None:
        if ma5["distance_pct"] > 0 and ma10["distance_pct"] > 0:
            summary = "短线仍在5日线和10日线上方，趋势没有完全破坏。"
        elif ma5["distance_pct"] < 0 and ma10["distance_pct"] < 0:
            summary = "短线已经跌破5日线和10日线，先按弱势或分歧处理。"
        else:
            summary = "当前在5日线和10日线之间，短线方向还需要确认。"
    else:
        summary = "均线数据暂不完整。"
    return {"items": items, "summary": summary, "above_count": len(above), "below_count": len(below)}


def _round_level(price: float) -> float:
    step = 5 if price >= 100 else 2 if price >= 50 else 1 if price >= 20 else 0.5 if price >= 10 else 0.2
    return round(round(price / step) * step, 2)


def _merge_levels(candidates: list[dict[str, Any]], current: float, side: str) -> list[dict[str, Any]]:
    filtered = [item for item in candidates if item.get("price")]
    if side == "support":
        filtered = [item for item in filtered if item["price"] <= current]
    else:
        filtered = [item for item in filtered if item["price"] >= current]
    filtered = sorted(filtered, key=lambda item: abs(item["price"] - current))
    merged: list[dict[str, Any]] = []
    for item in filtered:
        if item["price"] <= 0 or any(abs(item["price"] / row["price"] - 1) < 0.015 for row in merged):
            continue
        merged.append({**item, "price": round(item["price"], 2)})
        if len(merged) == 3:
            break
    return merged


def support_resistance(klines: list[Kline], position: dict[str, Any], current_price: float | None = None) -> dict[str, Any]:
    if not klines:
        return {"supports": [], "resistances": []}
    current = current_price or klines[-1].close
    latest = klines[-1]
    previous = klines[-2] if len(klines) >= 2 else latest
    lows5 = min(row.low for row in klines[-5:])
    highs5 = max(row.high for row in klines[-5:])
    supports = _merge_levels(
        [
            {"price": latest.low, "reason": "日内低点附近"},
            {"price": previous.low, "reason": "昨日低点"},
            {"price": lows5, "reason": "近5日低点"},
            {"price": position.get("low_20d"), "reason": "近20日低点"},
            {"price": position.get("low_60d"), "reason": "近60日低点"},
            {"price": position.get("low_120d"), "reason": "近120日低点"},
            {"price": position.get("ma10"), "reason": "10日均线"},
            {"price": position.get("ma20"), "reason": "20日均线"},
            {"price": position.get("ma60"), "reason": "60日均线"},
            {"price": _round_level(current * 0.98), "reason": "整数关口"},
        ],
        current,
        "support",
    )
    resistances = _merge_levels(
        [
            {"price": latest.high, "reason": "日内高点附近"},
            {"price": previous.high, "reason": "昨日高点"},
            {"price": highs5, "reason": "近5日高点"},
            {"price": position.get("high_20d"), "reason": "近20日高点"},
            {"price": position.get("high_60d"), "reason": "近60日高点"},
            {"price": position.get("high_120d"), "reason": "近120日高点"},
            {"price": position.get("ma5"), "reason": "5日均线"},
            {"price": position.get("ma10"), "reason": "10日均线"},
            {"price": position.get("ma20"), "reason": "20日均线"},
            {"price": position.get("stage_high"), "reason": "阶段高点"},
            {"price": _round_level(current * 1.03), "reason": "整数关口"},
        ],
        current,
        "resistance",
    )
    for idx, item in enumerate(supports, 1):
        item["label"] = f"第{idx}支撑"
    for idx, item in enumerate(resistances, 1):
        item["label"] = f"第{idx}压力"
    return {"supports": supports, "resistances": resistances}


def judge_status(klines: list[Kline], position: dict[str, Any]) -> str:
    if len(klines) < 60:
        return "数据不足"
    price = klines[-1].close
    ma5, ma10, ma20, ma60 = position.get("ma5"), position.get("ma10"), position.get("ma20"), position.get("ma60")
    pct20 = _pct(klines[-20].close, price) or 0
    pct60 = _pct(klines[-60].close, price) or 0
    drawdown = position.get("drawdown_from_stage_high_pct") or 0
    avg_amount = sum((row.amount or row.volume) for row in klines[-6:-1]) / 5 if len(klines) >= 6 else 0
    volume_ratio = (klines[-1].amount or klines[-1].volume) / avg_amount if avg_amount else 1
    if ma5 and ma10 and ma20 and price > ma5 > ma10 > ma20 and pct20 > 0:
        return "强趋势"
    if pct60 > 80 and drawdown < -20 and ma20 and price < ma20 and volume_ratio > 1.2:
        return "高位退潮"
    if pct60 > 50 and -30 <= drawdown <= -10 and ma5 and price < ma5:
        return "高位分歧"
    if ma20 and ma60 and price < ma20 < ma60 and volume_ratio > 1.05:
        return "破位走弱"
    if ma20 and abs(price / ma20 - 1) <= 0.05 and abs(pct20) < 12:
        return "震荡整理"
    if ma20 and price > ma20 and drawdown < -35:
        return "低位修复"
    return "震荡整理"


def score_analysis(klines: list[Kline], position: dict[str, Any], levels: dict[str, Any], status: str, financial_score: int | None) -> dict[str, Any]:
    if not klines:
        return {"trend_score": None, "risk_score": None, "fundamental_score": financial_score, "buy_point_score": None, "volatility_score": None, "overall_score": None}
    price = klines[-1].close
    pct20 = _pct(klines[-20].close, price) if len(klines) >= 20 else 0
    pct60 = _pct(klines[-60].close, price) if len(klines) >= 60 else 0
    trend = 50
    trend += 15 if position.get("ma5") and price > position["ma5"] else -8
    trend += 15 if position.get("ma20") and price > position["ma20"] else -12
    trend += min(max((pct20 or 0), -30), 30) * 0.5
    drawdown = abs(position.get("drawdown_from_stage_high_pct") or 0)
    risk = min(100, max(0, 30 + max((pct60 or 0) - 40, 0) * 0.5 + drawdown * 0.8 + (20 if status in {"高位退潮", "破位走弱"} else 0)))
    support = levels["supports"][0]["price"] if levels["supports"] else None
    resistance = levels["resistances"][0]["price"] if levels["resistances"] else None
    buy = 45
    if support:
        dist_support = abs(price / support - 1) * 100
        buy += 25 if dist_support <= 3 else 10 if dist_support <= 8 else -5
    if resistance and price / resistance > 0.97:
        buy -= 15
    if status in {"高位退潮", "破位走弱"}:
        buy -= 15
    avg_amp = sum((row.amplitude or abs(row.change_pct or 0)) for row in klines[-20:]) / min(20, len(klines))
    volatility = min(100, max(0, round(35 + avg_amp * 8 + abs(pct20 or 0))))
    scores = {
        "trend_score": round(max(0, min(100, trend))),
        "risk_score": round(risk),
        "fundamental_score": financial_score,
        "buy_point_score": round(max(0, min(100, buy))),
        "volatility_score": volatility,
    }
    weighted = [(scores["trend_score"], 0.25), (scores["buy_point_score"], 0.2), (100 - scores["risk_score"], 0.2), (scores["volatility_score"], 0.1)]
    if financial_score is not None:
        weighted.append((financial_score, 0.2))
    denom = sum(weight for _, weight in weighted)
    scores["overall_score"] = round(sum(value * weight for value, weight in weighted) / denom)
    return scores


def _fundamental_score(code: str) -> int | None:
    years = fetch_financial_years(code)
    if not years:
        return None
    latest = years[-1]
    previous = years[-2] if len(years) >= 2 else latest
    score = 45
    if latest.roe is not None:
        score += 20 if latest.roe >= 15 else 10 if latest.roe >= 8 else -5
    if previous.net_profit and latest.net_profit:
        score += 15 if latest.net_profit > previous.net_profit else -10
    if latest.free_cash_flow is not None:
        score += 10 if latest.free_cash_flow > 0 else -5
    return round(max(0, min(100, score)))


def _level_price(levels: dict[str, Any], side: str, index: int = 0) -> float | None:
    rows = levels.get(side) or []
    if len(rows) <= index:
        return None
    return rows[index].get("price")


def _ma_signal(ma_signals: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in ma_signals.get("items", []) if item.get("name") == name), None)


def _dist_pct(price: float | None, level: float | None) -> float | None:
    if price is None or not level:
        return None
    return round((price / level - 1) * 100, 2)


def _signal(code: str, title: str, direction: str, strength: int, detail: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": code,
        "title": title,
        "direction": direction,
        "strength": max(1, min(5, strength)),
        "detail": detail,
        "data": data,
    }


def build_signals(
    quote: dict[str, Any],
    position: dict[str, Any],
    levels: dict[str, Any],
    ma_signals: dict[str, Any],
    status: str,
    scores: dict[str, Any],
) -> list[dict[str, Any]]:
    price = quote.get("price")
    change_pct = quote.get("change_pct")
    turnover = quote.get("turnover_rate")
    support1 = _level_price(levels, "supports", 0)
    resistance1 = _level_price(levels, "resistances", 0)
    ma5 = _ma_signal(ma_signals, "MA5") or {}
    ma10 = _ma_signal(ma_signals, "MA10") or {}
    ma20 = _ma_signal(ma_signals, "MA20") or {}
    drawdown = position.get("drawdown_from_stage_high_pct")
    risk_score = scores.get("risk_score")
    buy_score = scores.get("buy_point_score")
    trend_score = scores.get("trend_score")
    signals: list[dict[str, Any]] = []

    below_ma5 = (ma5.get("distance_pct") or 0) < -0.5
    below_ma10 = (ma10.get("distance_pct") or 0) < -0.5
    above_ma5 = (ma5.get("distance_pct") or 0) > 0.5
    above_ma10 = (ma10.get("distance_pct") or 0) > 0.5
    above_ma20 = (ma20.get("distance_pct") or 0) > 0.5

    if below_ma5 and below_ma10:
        signals.append(_signal("ma_short_break", "短线均线转弱", "bearish", 4, f"当前价低于MA5({ma5.get('price')})和MA10({ma10.get('price')})，短线修复前不宜激进。", {"ma5": ma5, "ma10": ma10}))
    elif above_ma5 and above_ma10:
        signals.append(_signal("ma_short_above", "短线均线仍在上方", "bullish", 3, f"当前价站在MA5({ma5.get('price')})和MA10({ma10.get('price')})上方，短线结构暂未破坏。", {"ma5": ma5, "ma10": ma10}))
    else:
        signals.append(_signal("ma_short_mixed", "短线均线分歧", "neutral", 2, "当前价处在MA5和MA10附近，方向需要继续确认。", {"ma5": ma5, "ma10": ma10}))

    dist_support = _dist_pct(price, support1)
    if dist_support is not None:
        if 0 <= dist_support <= 3:
            signals.append(_signal("near_support", "靠近第一支撑", "bullish", 3, f"当前价距离第一支撑{support1}约{dist_support}%，适合观察承接，不适合跌破后继续摊低。", {"support": support1, "distance_pct": dist_support}))
        elif dist_support < 0:
            signals.append(_signal("support_broken", "跌破第一支撑", "bearish", 5, f"当前价已低于第一支撑{support1}，短线风险扩大。", {"support": support1, "distance_pct": dist_support}))

    dist_resistance = _dist_pct(price, resistance1)
    if dist_resistance is not None:
        if -3 <= dist_resistance <= 0:
            signals.append(_signal("near_resistance", "接近第一压力", "bearish", 3, f"当前价距离第一压力{resistance1}约{abs(dist_resistance)}%，若不能放量突破，容易冲高回落。", {"resistance": resistance1, "distance_pct": dist_resistance}))
        elif dist_resistance > 0:
            signals.append(_signal("resistance_break", "突破第一压力", "bullish", 4, f"当前价已站上第一压力{resistance1}，需要观察能否维持在其上方。", {"resistance": resistance1, "distance_pct": dist_resistance}))

    if drawdown is not None:
        if drawdown <= -25:
            signals.append(_signal("large_drawdown", "阶段高点回撤较大", "bearish", 4, f"从阶段高点回撤约{abs(drawdown)}%，说明高位抛压已经出现。", {"drawdown_pct": drawdown, "stage_high": position.get("stage_high")}))
        elif drawdown <= -10:
            signals.append(_signal("normal_drawdown", "出现阶段回撤", "neutral", 2, f"从阶段高点回撤约{abs(drawdown)}%，需要看支撑是否有效。", {"drawdown_pct": drawdown, "stage_high": position.get("stage_high")}))

    if change_pct is not None:
        if change_pct <= -7:
            signals.append(_signal("big_intraday_drop", "当日跌幅较大", "bearish", 4, f"当日跌幅{change_pct}%，短线情绪偏弱。", {"change_pct": change_pct}))
        elif change_pct >= 7:
            signals.append(_signal("big_intraday_rise", "当日涨幅较大", "bullish", 3, f"当日涨幅{change_pct}%，追高需要看是否突破压力并站稳。", {"change_pct": change_pct}))

    if turnover is not None:
        if turnover >= 10:
            signals.append(_signal("high_turnover", "换手明显放大", "neutral", 3, f"换手率{turnover}%，说明分歧或交易热度较高。", {"turnover_rate": turnover}))
        elif turnover <= 1:
            signals.append(_signal("low_turnover", "换手偏低", "neutral", 2, f"换手率{turnover}%，活跃度偏低，突破或修复的确认度有限。", {"turnover_rate": turnover}))

    if risk_score is not None and risk_score >= 70:
        signals.append(_signal("risk_high", "风险分偏高", "bearish", 4, f"风险分{risk_score}，仓位上需要更保守。", {"risk_score": risk_score}))
    if buy_score is not None and buy_score >= 65 and risk_score is not None and risk_score < 65:
        signals.append(_signal("buy_point_ok", "买点条件相对较好", "bullish", 3, f"买点分{buy_score}，且风险分未明显过高，适合继续观察确认。", {"buy_point_score": buy_score, "risk_score": risk_score}))
    if trend_score is not None and trend_score <= 35:
        signals.append(_signal("trend_weak", "趋势分偏弱", "bearish", 3, f"趋势分{trend_score}，说明当前价格结构偏弱。", {"trend_score": trend_score}))
    elif trend_score is not None and trend_score >= 70 and above_ma20:
        signals.append(_signal("trend_strong", "趋势分偏强", "bullish", 3, f"趋势分{trend_score}，且站在MA20上方，趋势仍有惯性。", {"trend_score": trend_score, "ma20": ma20}))

    if status in {"高位退潮", "破位走弱"}:
        signals.append(_signal("status_weak", status, "bearish", 4, f"系统状态识别为{status}，优先考虑风险控制。", {"status": status}))
    elif status == "强趋势":
        signals.append(_signal("status_strong", "强趋势状态", "bullish", 3, "系统状态识别为强趋势，但仍需避免远离均线追高。", {"status": status}))

    return sorted(signals, key=lambda item: item["strength"], reverse=True)


def summarize_signal_bias(signals: list[dict[str, Any]]) -> dict[str, Any]:
    bullish = sum(item["strength"] for item in signals if item["direction"] == "bullish")
    bearish = sum(item["strength"] for item in signals if item["direction"] == "bearish")
    neutral = sum(item["strength"] for item in signals if item["direction"] == "neutral")
    if bearish >= bullish + 4:
        bias = "偏防守"
    elif bullish >= bearish + 4:
        bias = "偏积极"
    else:
        bias = "中性观察"
    return {"bias": bias, "bullish": bullish, "bearish": bearish, "neutral": neutral}


def build_actions(
    name: str,
    quote: dict[str, Any],
    position: dict[str, Any],
    levels: dict[str, Any],
    ma_signals: dict[str, Any],
    status: str,
    scores: dict[str, Any],
    signals: list[dict[str, Any]],
) -> dict[str, str]:
    price = quote.get("price")
    change_pct = quote.get("change_pct")
    support1 = _level_price(levels, "supports", 0)
    support2 = _level_price(levels, "supports", 1)
    resistance1 = _level_price(levels, "resistances", 0)
    resistance2 = _level_price(levels, "resistances", 1)
    ma5 = _ma_signal(ma_signals, "MA5") or {}
    ma10 = _ma_signal(ma_signals, "MA10") or {}
    ma20 = _ma_signal(ma_signals, "MA20") or {}
    risk_score = scores.get("risk_score") or 0
    buy_score = scores.get("buy_point_score") or 0
    trend_score = scores.get("trend_score") or 0
    drawdown = position.get("drawdown_from_stage_high_pct")
    dist_support = _dist_pct(price, support1)
    dist_resistance = _dist_pct(price, resistance1)
    below_ma5 = (ma5.get("distance_pct") or 0) < -0.5
    below_ma10 = (ma10.get("distance_pct") or 0) < -0.5
    above_ma20 = (ma20.get("distance_pct") or 0) > 0.5
    high_risk = risk_score >= 65 or status in {"高位退潮", "破位走弱"}
    bias = summarize_signal_bias(signals)["bias"]
    top_reasons = "；".join(item["title"] for item in signals[:3])

    if high_risk and below_ma5 and below_ma10:
        no_position = f"没买先不要追。当前信号偏防守（{top_reasons}），等重新站回MA5（{ma5.get('price')}元）或回踩{support1}元附近不再破位再观察。"
    elif dist_support is not None and 0 <= dist_support <= 3 and buy_score >= 55:
        no_position = f"没买可以只看小仓试错条件：价格离第一支撑{support1}元约{dist_support}%，若盘中不再破低且能收回MA5，可继续观察；跌破{support1}元则放弃。"
    elif dist_resistance is not None and -3 <= dist_resistance <= 0:
        no_position = f"没买不适合在压力位下方追。当前接近第一压力{resistance1}元，除非放量突破并站稳，否则容易冲高回落。"
    elif status == "强趋势" and trend_score >= 65:
        no_position = f"趋势仍偏强，但不要追瞬时拉升。更好的观察点是回踩MA5（{ma5.get('price')}元）不破，或突破{resistance1}元后能维持在其上方。"
    else:
        no_position = f"没买先等方向确认。当前综合信号为{bias}，上方看{resistance1}元能否突破，下方看{support1}元是否守住。"

    if high_risk:
        has_position = f"有仓先控风险。若跌破{support1}元且不能快速收回，说明短线承接弱；反弹到{resistance1}元附近但量能不足，可考虑降低仓位波动。"
    elif below_ma5 and below_ma10:
        has_position = f"有仓不宜硬扛短线波动。当前MA5/MA10都在上方，先看能否站回{ma5.get('price')}元；站不回就按{support1}元设观察线。"
    elif change_pct is not None and change_pct > 5 and dist_resistance is not None and dist_resistance > -2:
        has_position = f"有仓遇到大涨接近压力位，重点看{resistance1}元是否放量突破；冲高但不能站稳时，适合保护已有利润。"
    elif above_ma20 and risk_score < 55:
        has_position = f"有仓可以继续跟踪趋势。只要不有效跌破MA20（{ma20.get('price')}元）和第一支撑{support1}元，短线结构还没有明显破坏。"
    else:
        has_position = f"有仓按区间处理：{support1}元是短线防守位，{resistance1}元是第一观察压力；区间内不要频繁追涨杀跌。"

    if high_risk or (status == "高位分歧" and below_ma5):
        add_position = f"不建议补仓。当前风险分{risk_score}，且状态为{status}；只有重新站回MA10（{ma10.get('price')}元）并放量稳定后，再考虑小仓验证。"
    elif dist_support is not None and 0 <= dist_support <= 2 and not below_ma10:
        add_position = f"想加仓只适合靠近支撑的小仓试错。参考区间在{support1}元附近，跌破后不要摊低；如果直接拉到{resistance1}元附近，就不追。"
    elif buy_score >= 65 and trend_score >= 55:
        add_position = f"加仓条件相对可以，但仍要分批。优先等回踩MA5（{ma5.get('price')}元）或支撑{support1}元确认，而不是盘中急拉时追。"
    else:
        add_position = f"暂不适合主动加仓。买点分{buy_score}，趋势分{trend_score}，说明当前更多是观察位；等突破{resistance1}元或回踩{support1}元企稳再说。"

    if drawdown is not None and drawdown < -20:
        final = f"{name}已经从阶段高点回撤约{abs(drawdown)}%，当前重点不是预测反弹高度，而是确认{support1}元能否守住、MA5/MA10能否收复。"
    elif status == "强趋势":
        final = f"{name}趋势仍有惯性，关键是不要在远离均线时追高；用MA5和第一支撑做节奏线。"
    else:
        final = f"{name}当前属于{status}，综合信号为{bias}；更适合按关键价位做观察，不适合把某一个支撑或压力当成确定买卖点。"

    return {
        "action_no_position": no_position,
        "action_has_position": has_position,
        "action_add_position": add_position,
        "final_conclusion": final,
    }


def build_judgement(name: str, quote: dict[str, Any], position: dict[str, Any], levels: dict[str, Any], ma_signals: dict[str, Any], status: str, scores: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, str]:
    support = levels["supports"][0]["price"] if levels["supports"] else None
    resistance = levels["resistances"][0]["price"] if levels["resistances"] else None
    risk_score = scores.get("risk_score") or 0
    risk_level = "极高" if risk_score >= 80 else "高" if risk_score >= 65 else "中" if risk_score >= 40 else "低"
    summary_map = {
        "强趋势": "趋势还在，但追高要看量能和回踩位置。",
        "高位分歧": "前期涨幅较大，短线进入分歧，不适合盲目追涨。",
        "高位退潮": "高位回撤和均线破位同时出现，先控制风险。",
        "震荡整理": "暂时没有明确单边方向，适合等区间边界确认。",
        "破位走弱": "关键均线下方运行，风险优先级高于机会。",
        "低位修复": "有修复迹象，但还要继续确认量能和趋势延续。",
    }
    summary = f"{name}现在属于{status}。{summary_map.get(status, '数据不足，先观察关键价位。')}"
    support_text = f"{support}元" if support else "第一支撑"
    resistance_text = f"{resistance}元" if resistance else "第一压力"
    actions = build_actions(name, quote, position, levels, ma_signals, status, scores, signals)
    return {
        "summary": summary,
        "status": status,
        "risk_level": risk_level,
        "short_term": f"短线重点看{support_text}能否守住；重新站回{resistance_text}上方，修复才更明确。",
        "mid_term": "中线看20日线和60日线的相对位置；若重新站稳20日线并放量，趋势会更健康。",
        "long_term": "长期仍要回到业绩、行业景气和现金流验证，技术位只适合辅助判断节奏。",
        **actions,
    }


def build_simple_context(stock: StockListing, quote: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    profile = _cached(f"profile:{stock.code}", 60 * 60 * 6, lambda: fetch_company_profile(stock.code))
    announcements = _cached(f"announcements:{stock.code}", 60 * 20, lambda: fetch_announcements(stock.code, limit=3))

    business = "主营业务暂未取到，先按行情和技术位置观察。"
    if profile:
        main = profile.get("main_business") or profile.get("business_summary") or profile.get("description")
        industry = profile.get("industry")
        if main and industry:
            business = f"主要做{main}，所属行业偏{industry}。"
        elif main:
            business = f"主要做{main}。"

    latest = announcements[0] if announcements else None
    latest_notice = f"{latest['date']}：{latest['title']}" if latest else "近期未抓到明确公告标题。"

    titles = "；".join(item["title"] for item in announcements[:2])
    event_hint = ""
    if any(word in titles for word in ["分红", "权益分派", "利润分配", "回购", "增持"]):
        event_hint = "公告有分红、回购或增持类信息，可能增强短线情绪。"
    elif any(word in titles for word in ["减持", "问询", "监管", "诉讼", "亏损", "风险"]):
        event_hint = "公告有减持、问询、监管或风险类关键词，可能压制情绪。"

    change_pct = quote.get("change_pct")
    if event_hint:
        move_reason = event_hint
    elif change_pct is None:
        move_reason = "缺少涨跌幅数据，先看公告和关键价位。"
    elif change_pct > 2:
        move_reason = f"今天涨幅{change_pct}%，更像资金在交易修复或题材预期；能否延续看压力位能否站稳。"
    elif change_pct < -2:
        move_reason = f"今天跌幅{abs(change_pct)}%，更像资金在回避短线风险；没站回关键均线前先按弱势处理。"
    else:
        move_reason = f"今天涨跌幅{change_pct}%，波动不大，主要看支撑能否守住、压力能否放量突破。"

    if signals and not event_hint:
        move_reason = f"{move_reason} 盘面信号：{signals[0]['detail']}"

    return {"business": business, "latest_notice": latest_notice, "move_reason": move_reason}


def analyze_stock(keyword_or_code: str) -> dict[str, Any]:
    stock = resolve_stock(keyword_or_code)
    if not stock:
        return {"ok": False, "error": "未找到对应A股股票，请输入更准确的股票名称或6位代码。", "query": keyword_or_code}
    klines, kline_meta = get_daily_kline(stock.code, days=250)
    if len(klines) < 30:
        return {"ok": False, "error": "K线数据暂不可用，无法生成支撑压力分析。", "code": stock.code, "name": stock.name, "data_source": kline_meta}
    quote = get_quote(stock.code, klines)
    position = position_metrics(klines)
    ma_signals = moving_average_signals(klines, quote.get("price"))
    levels = support_resistance(klines, position, quote.get("price"))
    status = judge_status(klines, position)
    fundamental = _fundamental_score(stock.code)
    scores = score_analysis(klines, position, levels, status, fundamental)
    signals = build_signals(quote, position, levels, ma_signals, status, scores)
    judgement = build_judgement(stock.name, quote, position, levels, ma_signals, status, scores, signals)
    context = build_simple_context(stock, quote, signals)
    return {
        "ok": True,
        "code": stock.code,
        "name": stock.name,
        "market": _market(stock.code),
        "quote": quote,
        "position": position,
        "moving_averages": ma_signals,
        "levels": levels,
        "signals": signals,
        "signal_summary": summarize_signal_bias(signals),
        "scores": scores,
        "judgement": judgement,
        "context": context,
        "data_source": {"quote": quote.get("source"), "kline": kline_meta.get("source"), "update_time": quote.get("update_time")},
    }


def compare_stocks(stocks: list[str]) -> dict[str, Any]:
    items = []
    errors = []
    for item in stocks[:10]:
        query = item.strip()
        if not query:
            continue
        result = analyze_stock(query)
        if result.get("ok"):
            scores = result["scores"]
            items.append(
                {
                    "code": result["code"],
                    "name": result["name"],
                    "price": result["quote"].get("price"),
                    "change_pct": result["quote"].get("change_pct"),
                    "amount": result["quote"].get("amount"),
                    "amount_yi": result["quote"].get("amount_yi"),
                    "turnover_rate": result["quote"].get("turnover_rate"),
                    "overall_score": scores.get("overall_score"),
                    "risk_score": scores.get("risk_score"),
                    "buy_point_score": scores.get("buy_point_score"),
                    "trend_score": scores.get("trend_score"),
                    "volatility_score": scores.get("volatility_score"),
                    "status": result["judgement"].get("status"),
                    "summary": result["judgement"].get("summary"),
                }
            )
        else:
            errors.append({"query": query, "error": result.get("error")})

    def codes_by(key: str, reverse: bool = True) -> list[str]:
        return [row["code"] for row in sorted(items, key=lambda row: row.get(key) if row.get(key) is not None else -999, reverse=reverse)]

    rankings = {
        "overall": codes_by("overall_score"),
        "stability": codes_by("risk_score", reverse=False),
        "short_term_elasticity": codes_by("volatility_score"),
        "risk": codes_by("risk_score"),
        "buy_point": codes_by("buy_point_score"),
    }
    best = max(items, key=lambda row: row.get("overall_score") or -1) if items else None
    conclusion = f"当前综合看，{best['name']}相对靠前；排序只基于公开行情和技术指标，不代表买卖建议。" if best else "没有可比较的有效股票。"
    return {"items": items, "errors": errors, "rankings": rankings, "conclusion": conclusion}


def analyze_position(code_or_name: str, cost: float, shares: int | None = None) -> dict[str, Any]:
    result = analyze_stock(code_or_name)
    if not result.get("ok"):
        return result
    current = result["quote"].get("price")
    profit_pct = _pct(cost, current)
    levels = result["levels"]
    resistances = levels.get("resistances") or []
    supports = levels.get("supports") or []
    if current is not None and cost > current:
        cost_position = "成本位在当前价上方，反弹到成本附近容易遇到解套压力。"
    elif current is not None and cost < current:
        cost_position = "成本低于当前价，已有浮盈垫，重点是保护利润。"
    else:
        cost_position = "成本位接近当前价。"
    suggestion = f"当前浮盈浮亏约{profit_pct}%。" if profit_pct is not None else "暂时无法计算浮盈浮亏。"
    if profit_pct is not None and profit_pct < -8:
        suggestion += " 亏损扩大时不要连续补仓，先看第一支撑是否守住。"
    elif profit_pct is not None and profit_pct > 10:
        suggestion += " 已有盈利，接近压力位且量能不足时可考虑降低波动。"
    else:
        suggestion += " 先按支撑压力做仓位管理。"
    if resistances:
        suggestion += f" 反弹重点看{resistances[0]['price']}元附近。"
    if supports:
        suggestion += f" 跌破{supports[0]['price']}元风险会放大。"
    return {
        "code": result["code"],
        "name": result["name"],
        "current_price": current,
        "cost": cost,
        "shares": shares,
        "profit_pct": profit_pct,
        "cost_position": cost_position,
        "suggestion": suggestion,
    }
