from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .company_profile import fetch_company_profile
from .data import Company, build_dynamic_a_share_company, build_placeholder_company, find_company
from .financials import fetch_financial_years
from .insights import (
    build_logic,
    business_breakdown,
    event_timeline,
    fair_value_range,
    message_impacts,
    quality_value_scores,
    risk_cards,
    risk_level,
    valuation_gap,
    score_color,
    valuation_label,
)
from .live_market import fetch_live_quote
from .scoring import score_company
from .stock_universe import find_a_share


def _secid(code: str) -> str:
    market = "1" if code.startswith(("6", "9")) else "0"
    return f"{market}.{code}"


def _today() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def _get_json(url: str, timeout: float = 6) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_announcements(code: str, limit: int = 8) -> list[dict[str, str]]:
    params = urlencode(
        {
            "sr": "-1",
            "page_size": limit,
            "page_index": 1,
            "ann_type": "A",
            "client_source": "web",
            "stock_list": code,
        }
    )
    try:
        payload = _get_json(f"https://np-anotice-stock.eastmoney.com/api/security/ann?{params}")
    except Exception:
        return []
    rows = (payload.get("data") or {}).get("list") or []
    return [
        {
            "date": str(item.get("notice_date") or item.get("display_time") or "")[:10],
            "title": str(item.get("title") or item.get("title_ch") or "未命名公告"),
            "type": "公告",
            "source": "东方财富公告接口",
            "url": f"https://data.eastmoney.com/notices/detail/{code}/{item.get('art_code')}.html" if item.get("art_code") else "",
        }
        for item in rows
    ]


def fetch_capital_flow(code: str) -> dict[str, Any] | None:
    params = urlencode({"secid": _secid(code), "fields": "f62,f66,f69,f72,f75,f78,f81,f84,f87"})
    try:
        payload = _get_json(f"https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get?{params}", timeout=4)
    except Exception:
        return None
    data = payload.get("data") or {}
    klines = data.get("klines") or []
    if not klines:
        return None
    latest = str(klines[-1]).split(",")
    return {"source": "东方财富资金流接口", "latest": latest}


def resolve_company(query: str) -> Company:
    listing = find_a_share(query)
    if listing:
        quote = fetch_live_quote(listing.code)
        return build_dynamic_a_share_company(
            code=listing.code,
            name=(quote or {}).get("name") or listing.name,
            price=(quote or {}).get("price") or listing.price,
            change_pct=(quote or {}).get("change_pct") or listing.change_pct,
            market_cap=(quote or {}).get("market_cap") or listing.market_cap,
            pe=(quote or {}).get("pe") or listing.pe,
            pb=(quote or {}).get("pb") or listing.pb,
        )
    quote = fetch_live_quote(query) if query.isdigit() else None
    if quote and quote.get("name"):
        return build_dynamic_a_share_company(
            code=quote["code"],
            name=quote["name"],
            price=quote.get("price"),
            change_pct=quote.get("change_pct"),
            market_cap=quote.get("market_cap"),
            pe=quote.get("pe"),
            pb=quote.get("pb"),
        )
    return build_placeholder_company(query)


def _infer_topics(company: Company, announcements: list[dict[str, str]]) -> list[str]:
    tokens = []
    for token in [company.name, company.industry, *company.sectors, *company.concepts, *(item["title"] for item in announcements)]:
        if "待AI" in token or token in {"AI搜索", "待接入数据源"}:
            continue
        tokens.append(token)
    text = " ".join(tokens)
    rules = [
        ("AI", ["AI", "算力", "服务器", "光模块", "大模型"]),
        ("半导体", ["半导体", "芯片", "晶圆", "硅片", "功率器件"]),
        ("新能源", ["新能源", "电池", "储能", "汽车", "锂"]),
        ("消费", ["消费", "白酒", "食品", "家电"]),
        ("金融", ["银行", "保险", "金融", "券商"]),
        ("分红", ["分红", "权益分派", "利润分配"]),
        ("风险提示", ["诉讼", "减持", "亏损", "问询", "监管"]),
    ]
    topics = [name for name, keywords in rules if any(keyword in text for keyword in keywords)]
    return topics or ["待进一步识别"]


def _score_research(company: Company, quote: dict[str, Any] | None, announcements: list[dict[str, str]], topics: list[str]) -> dict[str, Any]:
    if not company.is_placeholder:
        return score_company(company)
    pe = quote.get("pe") if quote else company.pe
    pb = quote.get("pb") if quote else company.pb
    score = 35
    reasons = []
    if quote and quote.get("market_cap"):
        score += 10
        reasons.append(f"已获取实时市值{quote['market_cap']}亿元")
    if pe is not None and pe > 0:
        score += 10 if pe < 25 else 5
        reasons.append(f"已获取PE {pe}")
    if pb is not None and pb > 0:
        score += 8 if pb < 3 else 4
        reasons.append(f"已获取PB {pb}")
    if announcements:
        score += min(12, len(announcements) * 2)
        reasons.append(f"最近公告样本{len(announcements)}条")
    if "风险提示" in topics:
        score -= 8
        reasons.append("公告标题出现风险相关关键词")
    total = max(0, min(100, score))
    return {
        "total": total,
        "items": [
            {"name": "数据完整度", "score": min(25, 10 + len(announcements) * 2), "max": 25, "reasons": reasons or ["仅获取到基础股票池信息"]},
            {
                "name": "估值可读性",
                "score": 20 if pe and pe > 0 else 8,
                "max": 25,
                "reasons": [item for item in [f"PE={pe}" if pe else None, f"PB={pb}" if pb else None, "估值字段暂未完整取得" if not pe and not pb else None] if item],
            },
            {"name": "消息透明度", "score": min(25, len(announcements) * 3), "max": 25, "reasons": [item["title"] for item in announcements[:3]] or ["暂无公告样本"]},
            {"name": "风险可识别性", "score": 12 if "风险提示" in topics else 20, "max": 25, "reasons": topics},
        ],
        "verdict": "动态研究报告已生成；深度财务评分仍需接入完整财报数据。",
    }


def build_research_report(query: str) -> dict[str, Any]:
    company = resolve_company(query)
    quote = fetch_live_quote(company.code) if company.code.isdigit() else None
    profile = fetch_company_profile(company.code) if company.code.isdigit() else None
    announcements = fetch_announcements(company.code) if company.code.isdigit() else []
    capital_flow = fetch_capital_flow(company.code) if company.code.isdigit() else None
    financial_years = fetch_financial_years(company.code) if company.code.isdigit() else []
    topics = _infer_topics(company, announcements)
    if profile:
        for concept in profile.get("concepts") or []:
            if concept not in topics and len(topics) < 6:
                topics.append(concept)
    if len(topics) > 1 and "待进一步识别" in topics:
        topics = [topic for topic in topics if topic != "待进一步识别"]
    pe = quote.get("pe") if quote else company.pe
    pb = quote.get("pb") if quote else company.pb
    valuation = valuation_label(pe, pb)
    score = _score_research(company, quote, announcements, topics)
    top_announcements = announcements[:5]

    financial_dicts = [
        {
            "year": item.year,
            "revenue": item.revenue,
            "net_profit": item.net_profit,
            "gross_margin": item.gross_margin,
            "net_margin": item.net_margin,
            "roe": item.roe,
            "free_cash_flow": item.free_cash_flow,
            "debt_ratio": item.debt_ratio,
            "eps": item.eps,
        }
        for item in financial_years
    ]
    logic = build_logic(
        name=company.name,
        industry=(profile or {}).get("industry") or company.industry,
        topics=topics,
        valuation=valuation,
        financials=financial_dicts,
        announcements=top_announcements,
    )
    qv_scores = quality_value_scores(
        score["total"],
        pe,
        pb,
        financial_dicts[-1].get("roe") if financial_dicts else None,
        (
            round((financial_dicts[-1]["net_profit"] / financial_dicts[-2]["net_profit"] - 1) * 100, 1)
            if len(financial_dicts) >= 2 and financial_dicts[-2].get("net_profit")
            else None
        ),
    )

    reference_range = fair_value_range(quote.get("price") if quote else None, pe, pb)
    price_gap = valuation_gap(quote.get("price") if quote else None, reference_range)

    summary = [
        f"{company.name}（{company.code}）已完成自动研究资料收集。",
        f"当前识别主题：{'、'.join(topics)}。",
        f"估值初判：{valuation}，{price_gap}。",
        f"一句话结论：{logic['one_sentence']}",
    ]
    if profile and profile.get("main_business"):
        summary.insert(1, f"主营业务：{profile['main_business']}")
    if quote and quote.get("price") is not None:
        summary.append(f"实时价{quote['price']}，当日涨跌幅{quote.get('change_pct', '--')}%。")
    if top_announcements:
        summary.append(f"最近公告中需要优先阅读：{top_announcements[0]['title']}。")
    if financial_years:
        latest_fin = financial_years[-1]
        summary.append(
            f"最近年报口径：营收{latest_fin.revenue}亿元，归母净利润{latest_fin.net_profit}亿元，ROE {latest_fin.roe}%。"
        )

    risks = []
    if company.is_placeholder:
        if financial_years:
            risks.append("已拉取年报核心财务指标，但研发投入、现金储备和分部收入仍需继续解析年报正文。")
        else:
            risks.append("当前缺少近五年完整财务指标，盈利趋势、ROE和现金流评分仍不能最终确认。")
    if not company.is_placeholder:
        risks.extend(item["detail"] for item in company.risks[:3])
    if pe is not None and pe <= 0:
        risks.append("PE为负或不可用，说明利润可能为负或估值指标暂时失真。")
    elif pe is not None and pe > 45:
        risks.append("PE较高，后续增长或盈利修复不及预期时估值回撤风险更大。")
    if any("减持" in item["title"] for item in announcements):
        risks.append("公告标题出现减持信息，需要进一步阅读减持主体、数量和期限。")
    if any("问询" in item["title"] or "监管" in item["title"] for item in announcements):
        risks.append("公告标题出现问询或监管关键词，需要优先核查合规和信息披露风险。")

    sources = []
    if quote:
        sources.append({"name": "实时行情", "source": quote["source"], "url": "https://quote.eastmoney.com/"})
    if announcements:
        sources.append({"name": "公司公告", "source": "东方财富公告接口", "url": "https://data.eastmoney.com/notices/"})
    if capital_flow:
        sources.append({"name": "资金流", "source": capital_flow["source"], "url": "https://data.eastmoney.com/zjlx/"})

    return {
        "code": company.code,
        "name": company.name,
        "generated_at": _today().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "complete",
        "summary": summary,
        "topics": topics,
        "valuation": {
            "label": valuation,
            "pe": pe,
            "pb": pb,
            "market_cap": quote.get("market_cap") if quote else company.market_cap,
            "price": quote.get("price") if quote else None,
            "change_pct": quote.get("change_pct") if quote else None,
            "fair_value_range": reference_range,
            "valuation_gap": price_gap,
        },
        "header": {
            "ai_conclusion": logic["one_sentence"],
            "positioning": logic["positioning"],
            "risk_level": risk_level(
                pe,
                pb,
                financial_dicts[-1].get("debt_ratio") if financial_dicts else None,
                (
                    round((financial_dicts[-1]["net_profit"] / financial_dicts[-2]["net_profit"] - 1) * 100, 1)
                    if len(financial_dicts) >= 2 and financial_dicts[-2].get("net_profit")
                    else None
                ),
            ),
            "updated_at": _today().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "investment_logic": logic,
        "quality_scores": qv_scores,
        "risk_cards": risk_cards(pe, pb, financial_dicts, top_announcements),
        "event_timeline": event_timeline(top_announcements, financial_dicts),
        "business_breakdown": business_breakdown(profile, financial_dicts),
        "message_impacts": message_impacts(top_announcements),
        "message_groups": {
            "最新公告": top_announcements,
            "最新新闻": [],
            "机构评级": [],
            "政策影响": [],
        },
        "profile": profile,
        "announcements": top_announcements,
        "financials": financial_dicts,
        "risks": risks[:6],
        "score": score,
        "score_color": score_color(score["total"]),
        "sources": sources,
        "limitations": [
            "当前版本已自动接入股票池、行情估值和公告标题，并会在非样例股票打开后自动触发。",
            "完整财报、新闻正文、研报正文和同行自动识别仍需要继续接数据源或LLM抽取。",
            "本报告用于研究辅助，不提供买卖建议。",
        ],
    }
