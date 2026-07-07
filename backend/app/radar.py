from __future__ import annotations

from dataclasses import dataclass
import json
import shutil
import subprocess
from urllib.request import Request, urlopen
from typing import Any

from .data import HOT_SECTORS, all_companies
from .market import fetch_board_list, market_overview
from .stock_analysis import compare_stocks


@dataclass(frozen=True)
class ScoreBand:
    min_score: int
    label: str
    action: str


SCORE_BANDS = [
    ScoreBand(90, "重点关注", "只等合适买点，不盲目追高"),
    ScoreBand(80, "加入观察池", "跟踪板块和资金持续性"),
    ScoreBand(70, "一般关注", "先看不动，等形态更清楚"),
    ScoreBand(60, "只看不买", "条件不够完整，降低优先级"),
    ScoreBand(0, "暂不关注", "风险或强度不匹配"),
]

_STOCK_ROW_CACHE: dict[str, Any] = {"rows": None}


def _num(value: Any) -> float | None:
    if value in (None, "", "-", "--"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _yi(value: float | int | None) -> float | None:
    return round(float(value) / 100_000_000, 2) if value is not None else None


def _read_json(url: str, timeout: int = 10) -> dict[str, Any] | None:
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}
    try:
        with urlopen(Request(url, headers=headers), timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", errors="ignore"))
    except Exception:
        pass

    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        return None
    try:
        completed = subprocess.run(
            [curl, "-L", "-s", "--max-time", str(timeout), "-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://quote.eastmoney.com/", url],
            check=False,
            capture_output=True,
            text=False,
            timeout=timeout + 2,
        )
        if completed.stdout.strip():
            return json.loads(completed.stdout.decode("utf-8", errors="ignore"))
    except Exception:
        return None
    return None


def _fetch_a_stock_rows(force_refresh: bool = False) -> list[dict[str, Any]]:
    if _STOCK_ROW_CACHE["rows"] and not force_refresh:
        return _STOCK_ROW_CACHE["rows"]
    rows: list[dict[str, Any]] = []
    page = 1
    fields = "f2,f3,f6,f8,f12,f14,f15,f16,f17,f18,f20,f21,f62,f100"
    while True:
        url = (
            "https://push2.eastmoney.com/api/qt/clist/get"
            f"?pn={page}&pz=500&po=1&np=1&fltt=2&invt=2"
            "&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
            f"&fields={fields}"
        )
        payload = _read_json(url, timeout=12)
        data = (payload or {}).get("data") or {}
        diff = data.get("diff") or []
        rows.extend(diff)
        total = int(data.get("total") or len(rows))
        if len(rows) >= total or not diff:
            break
        page += 1
        if page > 20:
            break
    if rows:
        _STOCK_ROW_CACHE["rows"] = rows
    return rows


def _score_band(score: int | float | None) -> dict[str, str]:
    value = int(score or 0)
    for band in SCORE_BANDS:
        if value >= band.min_score:
            return {"label": band.label, "action": band.action}
    return {"label": "暂不关注", "action": "数据不足"}


def _emotion_score(overview: dict[str, Any]) -> int:
    avg_risk = float(overview.get("avg_risk") or 0)
    score = round(82 - avg_risk * 16)
    positives = 0
    for item in overview.get("items") or []:
        pct = ((item.get("quote") or {}).get("change_pct"))
        if pct is not None and pct > 0:
            positives += 1
    score += positives * 2
    return max(0, min(100, score))


def _emotion_label(score: int) -> str:
    if score >= 80:
        return "强势市场，可积极筛选"
    if score >= 60:
        return "正常市场，轻仓试错"
    if score >= 40:
        return "震荡市场，控制仓位"
    return "弱势市场，少操作"


def _hot_sectors(candidates: list[dict[str, Any]] | None = None, limit: int = 8) -> list[dict[str, Any]]:
    rows = _industry_sectors_from_stocks(limit=limit)
    if rows:
        return rows
    rows = _industry_sectors_from_candidates(candidates or [], limit=limit)
    if rows:
        return rows
    rows = [row for row in fetch_board_list() if row.get("name") and row.get("code")]
    if not rows:
        return [
            {
                "code": f"local-{index}",
                "name": name,
                "change_pct": round(1.8 - index * 0.25, 2),
                "amount_yi": round(180 - index * 12, 2),
                "main_net_inflow_yi": round(8 - index * 0.7, 2),
                "limit_up_count": max(0, 6 - index),
                "leader": "样例池待盘中确认",
                "catalyst": "实时板块接口未返回，使用本地热点方向给出估算参考",
                "heat_score": max(50, 76 - index * 3),
                "conclusion": "有长期关注度，需等待当日行情确认",
            }
            for index, name in enumerate(HOT_SECTORS[:limit])
        ]
    rows = sorted(rows, key=lambda row: row.get("change_pct") if row.get("change_pct") is not None else -999, reverse=True)[:limit]
    result = []
    for row in rows:
        change = row.get("change_pct") or 0
        score = max(0, min(100, round(45 + change * 8)))
        result.append(
            {
                "code": row.get("code"),
                "name": row.get("name"),
                "change_pct": row.get("change_pct"),
                "amount_yi": "接口未披露",
                "main_net_inflow_yi": "接口未披露",
                "limit_up_count": "待盘后确认",
                "leader": "待盘中识别",
                "catalyst": "公开板块行情显示涨幅靠前，消息催化需继续确认",
                "heat_score": score,
                "conclusion": "强热点，可优先看趋势中军" if score >= 80 else "有热度，继续观察持续性",
            }
        )
    return result


def _industry_sectors_from_stocks(limit: int = 8) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in _fetch_a_stock_rows():
        industry = row.get("f100")
        pct = _num(row.get("f3"))
        amount = _num(row.get("f6"))
        if not industry or industry == "-" or pct is None or amount is None:
            continue
        grouped.setdefault(industry, []).append(row)
    sectors = []
    for name, rows in grouped.items():
        if len(rows) < 3:
            continue
        total_amount = sum(_num(row.get("f6")) or 0 for row in rows)
        main_net = sum(_num(row.get("f62")) or 0 for row in rows)
        weighted_pct = sum((_num(row.get("f3")) or 0) * (_num(row.get("f6")) or 0) for row in rows) / total_amount if total_amount else 0
        limit_up = sum(1 for row in rows if (_num(row.get("f3")) or 0) >= 9.7)
        rising = sum(1 for row in rows if (_num(row.get("f3")) or 0) > 0)
        leader_row = max(rows, key=lambda row: _num(row.get("f3")) if _num(row.get("f3")) is not None else -999)
        heat_score = round(45 + weighted_pct * 6 + min(total_amount / 10_000_000_000, 20) + min(limit_up * 3, 20) + (10 if main_net > 0 else 0))
        heat_score = max(0, min(100, heat_score))
        sectors.append(
            {
                "code": name,
                "name": name,
                "change_pct": round(weighted_pct, 2),
                "amount_yi": _yi(total_amount),
                "main_net_inflow_yi": _yi(main_net),
                "limit_up_count": limit_up,
                "leader": f"{leader_row.get('f14')} {leader_row.get('f12')}",
                "catalyst": f"行业内{rising}/{len(rows)}只上涨，成交额约{_yi(total_amount)}亿，主力净流入约{_yi(main_net)}亿",
                "heat_score": heat_score,
                "conclusion": "强热点，可重点关注龙头和趋势中军" if heat_score >= 80 else "有热度，继续观察持续性",
            }
        )
    return sorted(sectors, key=lambda row: row["heat_score"], reverse=True)[:limit]


def _industry_sectors_from_candidates(candidates: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in candidates:
        industry = row.get("industry") or "样例股票池"
        grouped.setdefault(industry, []).append(row)
    sectors = []
    for name, rows in grouped.items():
        amount_yi = sum(_num(row.get("amount_yi")) or 0 for row in rows)
        main_net = sum((_num(row.get("change_pct")) or 0) * (row.get("amount_yi") or 0) * 0.08 for row in rows)
        avg_pct = sum(_num(row.get("change_pct")) or 0 for row in rows) / len(rows)
        limit_up = sum(1 for row in rows if (_num(row.get("change_pct")) or 0) >= 9.7)
        leader = max(rows, key=lambda row: _num(row.get("change_pct")) if _num(row.get("change_pct")) is not None else -999)
        heat_score = max(0, min(100, round(55 + avg_pct * 6 + min(amount_yi, 20) + limit_up * 5)))
        sectors.append(
            {
                "code": name,
                "name": name,
                "change_pct": round(avg_pct, 2),
                "amount_yi": round(amount_yi, 2),
                "main_net_inflow_yi": round(main_net, 2),
                "limit_up_count": limit_up,
                "leader": f"{leader.get('name')} {leader.get('code')}",
                "catalyst": f"样例池内{len(rows)}只股票聚合，成交额约{round(amount_yi, 2)}亿",
                "heat_score": heat_score,
                "conclusion": "样例池热度靠前，适合继续跟踪" if heat_score >= 70 else "样例池有关注度，等待确认",
            }
        )
    return sorted(sectors, key=lambda row: row["heat_score"], reverse=True)[:limit]


def _market_stats(candidates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = _fetch_a_stock_rows()
    traded = [row for row in rows if _num(row.get("f2")) is not None and _num(row.get("f3")) is not None]
    rising = sum(1 for row in traded if (_num(row.get("f3")) or 0) > 0)
    falling = sum(1 for row in traded if (_num(row.get("f3")) or 0) < 0)
    flat = max(0, len(traded) - rising - falling)
    limit_up = sum(1 for row in traded if (_num(row.get("f3")) or 0) >= 9.7)
    limit_down = sum(1 for row in traded if (_num(row.get("f3")) or 0) <= -9.7)
    failed = 0
    touched = 0
    for row in traded:
        high = _num(row.get("f15"))
        prev = _num(row.get("f18"))
        pct = _num(row.get("f3")) or 0
        if high and prev and high >= prev * 1.095:
            touched += 1
            if pct < 9.7:
                failed += 1
    amount = sum(_num(row.get("f6")) or 0 for row in traded)
    if not traded and candidates:
        rising = sum(1 for row in candidates if (_num(row.get("change_pct")) or 0) > 0)
        falling = sum(1 for row in candidates if (_num(row.get("change_pct")) or 0) < 0)
        limit_up = sum(1 for row in candidates if (_num(row.get("change_pct")) or 0) >= 9.7)
        limit_down = sum(1 for row in candidates if (_num(row.get("change_pct")) or 0) <= -9.7)
        amount_yi = round(sum(_num(row.get("amount_yi")) or 0 for row in candidates), 2)
        return {
            "limit_up_count": limit_up,
            "limit_down_count": limit_down,
            "failed_limit_rate": 0,
            "amount_yi": amount_yi,
            "rising_count": rising,
            "falling_count": falling,
            "flat_count": max(0, len(candidates) - rising - falling),
            "sample_count": len(candidates),
            "source": "样例股票池聚合",
        }
    return {
        "limit_up_count": limit_up,
        "limit_down_count": limit_down,
        "failed_limit_rate": round(failed / touched * 100, 1) if touched else 0,
        "amount_yi": _yi(amount),
        "rising_count": rising,
        "falling_count": falling,
        "flat_count": flat,
        "sample_count": len(traded),
        "source": "东方财富A股列表聚合",
    }


def _candidate_codes() -> list[str]:
    return [company.code for company in all_companies() if company.code and company.code.isdigit()][:10]


def _technical_label(item: dict[str, Any]) -> str:
    status = item.get("status") or ""
    if status in {"强趋势", "低位修复"}:
        return "强趋势"
    if status in {"破位走弱", "高位退潮"}:
        return "破位下跌"
    if item.get("trend_score") is not None and item["trend_score"] >= 70:
        return "趋势偏强"
    return "平台整理"


def _candidate_rows() -> list[dict[str, Any]]:
    data = compare_stocks(_candidate_codes())
    rows = []
    company_map = {company.code: company for company in all_companies()}
    for item in data.get("items") or []:
        overall = item.get("overall_score")
        band = _score_band(overall)
        risk = item.get("risk_score")
        buy = item.get("buy_point_score")
        company = company_map.get(item.get("code"))
        rows.append(
            {
                **item,
                "industry": company.industry if company else "样例股票池",
                "grade": band["label"],
                "grade_action": band["action"],
                "technical_shape": _technical_label(item),
                "capital_state": "资金需继续确认",
                "message_state": "消息面待跟踪",
                "buy_signal": "等待买点",
                "risk_signal": "风险升高" if risk is not None and risk >= 70 else "风险可控",
                "candidate_reason": _candidate_reason(item),
                "watch_reason": f"{band['label']}：{item.get('summary') or ''}",
                "filtered_out": bool((risk is not None and risk >= 90) or (overall is not None and overall < 60)),
            }
        )
    return sorted(rows, key=lambda row: row.get("overall_score") if row.get("overall_score") is not None else -999, reverse=True)


def _candidate_reason(item: dict[str, Any]) -> str:
    status = item.get("status") or "状态待确认"
    score = item.get("overall_score")
    risk = item.get("risk_score")
    if risk is not None and risk >= 75:
        return f"{status}，但风险分{risk}偏高，先看风险释放。"
    if score is not None and score >= 80:
        return f"{status}，综合分{score}，适合加入观察池等待买点。"
    if score is not None and score >= 70:
        return f"{status}，有一定关注价值，但需要板块和资金配合。"
    return f"{status}，条件不够强，先降低优先级。"


def build_market_radar() -> dict[str, Any]:
    overview = market_overview()
    emotion = _emotion_score(overview)
    candidates = _candidate_rows()
    sectors = _hot_sectors(candidates)
    watch_suggestions = [row for row in candidates if not row["filtered_out"] and (row.get("overall_score") or 0) >= 70][:8]
    buy_signals = [row for row in candidates if row.get("buy_point_score") is not None and row["buy_point_score"] >= 65 and (row.get("risk_score") or 100) < 70]
    risk_rows = [row for row in candidates if row.get("risk_score") is not None and row["risk_score"] >= 70]
    return {
        "market": {
            "emotion_score": emotion,
            "emotion_label": _emotion_label(emotion),
            "state": overview.get("state"),
            "avg_risk": overview.get("avg_risk"),
            "indices": overview.get("items") or [],
            "advice": _market_advice(emotion),
            "stats": _market_stats(candidates),
        },
        "sectors": sectors,
        "candidates": candidates,
        "summary": {
            "focus_count": len(watch_suggestions),
            "buy_signal_count": len(buy_signals),
            "risk_count": len(risk_rows),
            "focus_directions": [row["name"] for row in sectors[:3]],
            "suggestion": _summary_suggestion(emotion, sectors, watch_suggestions, risk_rows),
        },
    }


def _market_advice(score: int) -> str:
    if score >= 80:
        return "市场情绪偏强，可重点筛热点板块里的趋势中军。"
    if score >= 60:
        return "市场情绪正常，适合轻仓试错，优先观察高评分低风险股票。"
    if score >= 40:
        return "市场震荡，先建观察池，等回踩或放量突破。"
    return "市场偏弱，风险提示优先级高于买点提示。"


def _summary_suggestion(emotion: int, sectors: list[dict[str, Any]], watch: list[dict[str, Any]], risks: list[dict[str, Any]]) -> str:
    direction = "、".join(row["name"] for row in sectors[:3]) or "热点待确认"
    if emotion < 40:
        return f"市场偏弱，少操作；可先观察{direction}，不追高。"
    if risks and len(risks) >= len(watch):
        return f"风险升高股票较多，重点看{direction}中的趋势中军，等待买点。"
    return f"控制仓位，重点关注{direction}等热点板块中的趋势中军。"
