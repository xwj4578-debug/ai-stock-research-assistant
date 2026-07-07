from __future__ import annotations

from typing import Any


def valuation_label(pe: float | None, pb: float | None) -> str:
    if pe is None and pb is None:
        return "估值数据不足"
    if pe is not None and pe <= 0:
        return "利润为负或PE失真"
    if pe is not None and pe < 12 and (pb is None or pb < 1.5):
        return "低估值"
    if pe is not None and pe > 45:
        return "高估值或高成长预期"
    if pb is not None and pb > 6:
        return "PB偏高"
    return "估值中性"


def fair_value_range(price: float | None, pe: float | None, pb: float | None) -> str:
    if not price or not pe or pe <= 0:
        return "数据不足，暂不估算"
    eps = price / pe
    if pe < 15:
        low_pe, high_pe = 10, 18
    elif pe < 35:
        low_pe, high_pe = 18, 30
    elif pe < 60:
        low_pe, high_pe = 25, 45
    else:
        low_pe, high_pe = 35, 70
    low, high = eps * low_pe, eps * high_pe
    if pb and pb > 6:
        high *= 0.85
    return f"{low:.2f} - {high:.2f} 元"


def valuation_gap(price: float | None, fair_range: str) -> str:
    if not price or " - " not in fair_range:
        return "数据不足"
    try:
        high = float(fair_range.split(" - ")[1].replace("元", "").strip())
    except (ValueError, IndexError):
        return "数据不足"
    if high <= 0:
        return "数据不足"
    diff = (price / high - 1) * 100
    if diff > 0:
        return f"当前价高于参考区间上沿约{diff:.1f}%"
    return f"当前价低于参考区间上沿约{abs(diff):.1f}%"


def risk_level(pe: float | None, pb: float | None, debt_ratio: float | None, profit_growth: float | None) -> str:
    score = 0
    if pe is not None and (pe <= 0 or pe > 60):
        score += 2
    elif pe is not None and pe > 40:
        score += 1
    if pb is not None and pb > 6:
        score += 1
    if debt_ratio is not None and debt_ratio > 65:
        score += 1
    if profit_growth is not None and profit_growth < -20:
        score += 2
    elif profit_growth is not None and profit_growth < 0:
        score += 1
    if score >= 3:
        return "高"
    if score >= 1:
        return "中"
    return "低"


def score_color(score: int | float) -> str:
    if score >= 90:
        return "deep-green"
    if score >= 80:
        return "green"
    if score >= 70:
        return "yellow"
    if score >= 60:
        return "orange"
    return "red"


def quality_value_scores(total_score: int | float, pe: float | None, pb: float | None, roe: float | None, profit_growth: float | None) -> dict[str, int]:
    quality = 50
    value = 50
    if roe is not None:
        quality += 20 if roe >= 15 else 10 if roe >= 8 else -5
    if profit_growth is not None:
        quality += 15 if profit_growth > 15 else 8 if profit_growth > 0 else -10
    quality = max(0, min(100, round((quality + total_score) / 2)))

    if pe is not None:
        if pe <= 0:
            value -= 20
        elif pe < 15:
            value += 20
        elif pe < 35:
            value += 5
        else:
            value -= 15
    if pb is not None:
        if pb < 2:
            value += 10
        elif pb > 6:
            value -= 15
    value = max(0, min(100, value))
    return {"quality": quality, "investment_value": value}


def build_logic(
    name: str,
    industry: str,
    topics: list[str],
    valuation: str,
    financials: list[dict[str, Any]],
    announcements: list[dict[str, str]],
) -> dict[str, Any]:
    latest = financials[-1] if financials else {}
    previous = financials[-2] if len(financials) >= 2 else {}
    profit_growth = None
    if latest.get("net_profit") is not None and previous.get("net_profit"):
        profit_growth = round((latest["net_profit"] / previous["net_profit"] - 1) * 100, 1)

    positives = []
    negatives = []
    if profit_growth is not None:
        if profit_growth > 10:
            positives.append(f"归母净利润同比增长约{profit_growth}%")
        elif profit_growth < 0:
            negatives.append(f"归母净利润同比下降约{abs(profit_growth)}%")
    if latest.get("roe") and latest["roe"] >= 10:
        positives.append(f"ROE达到{latest['roe']}%")
    elif latest.get("roe") is not None and latest["roe"] < 6:
        negatives.append(f"ROE仅{latest['roe']}%")
    if "分红" in topics:
        positives.append("近期公告涉及分红或权益分派")
    if "风险提示" in topics:
        negatives.append("公告标题出现风险相关关键词")
    if "高估值" in valuation or "PB偏高" in valuation:
        negatives.append(valuation)
    elif "低估值" in valuation:
        positives.append("估值处于低位区间")

    if not positives:
        positives.append("已接入公司资料、行情、公告和核心财务，研究数据完整度提升")
    if not negatives:
        negatives.append("未发现明确风险公告，但仍需继续跟踪财报正文和行业变化")

    status = "增强" if len(positives) > len(negatives) else "减弱" if len(negatives) > len(positives) else "中性"
    long_term = "适合持续跟踪" if status != "减弱" and "高估值" not in valuation else "适合观察，等待估值或业绩确认"
    conclusion = f"{name}属于{industry or '待识别行业'}公司，当前投资逻辑{status}，{valuation}，{long_term}。"

    return {
        "status": status,
        "positives": positives[:5],
        "negatives": negatives[:5],
        "long_term_view": long_term,
        "one_sentence": conclusion,
        "positioning": f"{industry or 'A股'} / {'、'.join(topics[:3]) if topics else '主题待识别'}",
    }


def risk_cards(pe: float | None, pb: float | None, financials: list[dict[str, Any]], announcements: list[dict[str, str]]) -> list[dict[str, str]]:
    latest = financials[-1] if financials else {}
    previous = financials[-2] if len(financials) >= 2 else {}
    cards = []
    if pe is not None and pe > 45:
        cards.append({
            "name": "估值回撤风险",
            "level": "高" if pe > 80 else "中",
            "probability": "中高",
            "impact": "高",
            "reason": f"当前PE为{pe}，市场对未来增长要求较高，业绩不及预期时容易压缩估值。",
        })
    if pb is not None and pb > 6:
        cards.append({
            "name": "PB偏高风险",
            "level": "中",
            "probability": "中",
            "impact": "中",
            "reason": f"当前PB为{pb}，资产定价已包含较多成长预期。",
        })
    if latest.get("net_profit") is not None and previous.get("net_profit"):
        growth = round((latest["net_profit"] / previous["net_profit"] - 1) * 100, 1)
        if growth < 0:
            cards.append({
                "name": "盈利下滑风险",
                "level": "高" if growth < -20 else "中",
                "probability": "已发生",
                "impact": "高",
                "reason": f"最近年报归母净利润同比下降{abs(growth)}%，需要确认是周期性波动还是竞争力变化。",
            })
    if any(any(word in item["title"] for word in ["减持", "问询", "监管", "诉讼"]) for item in announcements):
        cards.append({
            "name": "公告事件风险",
            "level": "中",
            "probability": "中",
            "impact": "中",
            "reason": "近期公告标题出现减持、问询、监管或诉讼等关键词，需要阅读公告正文确认影响。",
        })
    if not cards:
        cards.append({
            "name": "信息不足风险",
            "level": "中",
            "probability": "中",
            "impact": "中",
            "reason": "当前自动研究已覆盖行情、F10资料、公告和核心财务，但研报、新闻正文、分部收入仍未完整接入。",
        })
    return cards[:5]


def event_timeline(announcements: list[dict[str, str]], financials: list[dict[str, Any]]) -> list[dict[str, str]]:
    events = []
    for item in announcements[:6]:
        impact = "中性"
        if any(word in item["title"] for word in ["分红", "权益分派", "利润分配"]):
            impact = "偏利好"
        if any(word in item["title"] for word in ["减持", "问询", "监管", "诉讼"]):
            impact = "偏利空"
        events.append({"date": item["date"], "title": item["title"], "impact": impact, "url": item.get("url", "")})
    if financials:
        latest = financials[-1]
        events.insert(0, {
            "date": str(latest["year"]),
            "title": f"年报核心指标：营收{latest['revenue']}亿，净利润{latest['net_profit']}亿，ROE {latest['roe']}%",
            "impact": "财务",
            "url": "",
        })
    return events[:8]


def business_breakdown(profile: dict[str, Any] | None, financials: list[dict[str, Any]]) -> dict[str, Any]:
    latest = financials[-1] if financials else {}
    previous = financials[-2] if len(financials) >= 2 else {}
    revenue_growth = None
    profit_growth = None
    if latest.get("revenue") is not None and previous.get("revenue"):
        revenue_growth = round((latest["revenue"] / previous["revenue"] - 1) * 100, 1)
    if latest.get("net_profit") is not None and previous.get("net_profit"):
        profit_growth = round((latest["net_profit"] / previous["net_profit"] - 1) * 100, 1)
    return {
        "income_sources": (profile or {}).get("products") or ["主营业务待识别"],
        "profit_sources": [
            f"最近年报净利率{latest.get('net_margin')}%" if latest.get("net_margin") is not None else "利润率待接入",
            f"毛利率{latest.get('gross_margin')}%" if latest.get("gross_margin") is not None else "毛利率待接入",
        ],
        "fastest_growth": f"营收同比{revenue_growth}%" if revenue_growth is not None else "需解析分部收入后判断",
        "highest_margin": "需解析分部毛利率后判断",
        "future_growth": (profile or {}).get("growth_drivers") or ["未来增长点待识别"],
        "profit_growth": profit_growth,
        "revenue_growth": revenue_growth,
    }


def message_impacts(announcements: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for item in announcements[:6]:
        title = item["title"]
        if any(word in title for word in ["分红", "权益分派", "利润分配"]):
            effect, horizon = "偏利好", "短期现金回报/长期股东回报"
            why = "涉及利润分配或权益分派，影响股东回报预期。"
        elif any(word in title for word in ["股东会", "董事会"]):
            effect, horizon = "中性", "短期治理事项"
            why = "属于治理程序或会议决议，需要关注具体议案。"
        elif any(word in title for word in ["减持", "问询", "监管", "诉讼"]):
            effect, horizon = "偏利空", "短中期风险"
            why = "标题包含风险事件关键词，需要阅读公告正文确认影响。"
        else:
            effect, horizon = "中性", "需继续跟踪"
            why = "公告标题未显示明确利好或利空，需结合正文判断。"
        rows.append({**item, "effect": effect, "horizon": horizon, "why": why})
    return rows


def peer_summary(peers: list[dict[str, Any]]) -> str:
    if not peers:
        return "暂未形成可靠同行列表，避免展示误导性比较。"
    best_roe = max(peers, key=lambda item: item.get("roe") or -999)
    low_pe = min([item for item in peers if item.get("pe") and item["pe"] > 0], key=lambda item: item["pe"], default=None)
    best_score = max(peers, key=lambda item: item.get("score") or -999)
    parts = [f"ROE最高的是{best_roe['name']}（{best_roe.get('roe')}%）", f"综合评分最高的是{best_score['name']}（{best_score.get('score')}分）"]
    if low_pe:
        parts.append(f"PE最低的是{low_pe['name']}（{low_pe.get('pe')}）")
    return "；".join(parts) + "。"
