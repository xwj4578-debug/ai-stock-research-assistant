from __future__ import annotations

from dataclasses import asdict
from statistics import mean

from .data import Company


WEIGHTS = {
    "商业模式": 20,
    "行业景气": 15,
    "盈利能力": 20,
    "成长能力": 15,
    "估值水平": 10,
    "财务健康": 10,
    "风险控制": 5,
    "消息面": 5,
}


def _clamp(value: float, maximum: int) -> int:
    return max(0, min(maximum, round(value)))


def _cagr(start: float, end: float, years: int) -> float:
    if start <= 0 or end <= 0 or years <= 0:
        return 0
    return (end / start) ** (1 / years) - 1


def score_company(company: Company) -> dict:
    if company.is_placeholder:
        financials = company.financials or []
        has_real_financials = any(item.revenue or item.net_profit or item.roe for item in financials)
        if has_real_financials:
            latest = financials[-1]
            previous = financials[-2] if len(financials) >= 2 else latest
            reasons = []
            items = []
            completeness_score = 18
            items.append({"name": "资料完整度", "score": completeness_score, "max": 20, "reasons": ["已取得近五年核心财务数据"]})
            if latest.roe:
                reasons.append(f"最新ROE为{latest.roe}%")
            profitability_score = min(20, round((latest.roe or 0) / 1.2))
            items.append({"name": "盈利能力", "score": profitability_score, "max": 20, "reasons": [f"最新ROE为{latest.roe}%"]})
            if previous.net_profit and latest.net_profit:
                growth = (latest.net_profit / previous.net_profit - 1) * 100
                reasons.append(f"最近一年净利润同比{growth:.1f}%")
                growth_score = 16 if growth > 20 else 12 if growth > 0 else 6
            else:
                growth_score = 6
            items.append({"name": "成长能力", "score": growth_score, "max": 20, "reasons": reasons[:2] or ["财务趋势仍需观察"]})
            if latest.free_cash_flow:
                reasons.append(f"自由现金流为{latest.free_cash_flow}亿元")
            cash_score = 15 if latest.free_cash_flow and latest.free_cash_flow > 0 else 6
            items.append({"name": "现金质量", "score": cash_score, "max": 20, "reasons": [f"自由现金流为{latest.free_cash_flow}亿元"]})
            if company.news:
                reasons.append(f"已获取公告/消息{len(company.news)}条")
            if company.pe and company.pe > 0:
                reasons.append(f"PE为{company.pe}")
                valuation_score = 15 if company.pe < 35 else 8
                items.append({"name": "估值数据", "score": valuation_score, "max": 20, "reasons": [f"PE为{company.pe}"]})
            total = round(sum(item["score"] for item in items) / sum(item["max"] for item in items) * 100)
            return {
                "total": total,
                "items": items,
                "verdict": "已基于实时行情、公司资料和近五年核心财务生成初步质量分；缺失字段不展示、不冒充。",
            }
        return {
            "total": 0,
            "items": [{"name": name, "score": 0, "max": max_score, "reasons": ["未取得真实股票或财务数据。"]} for name, max_score in WEIGHTS.items()],
            "verdict": "未识别到可用真实数据，暂不打分。",
        }

    financials = company.financials
    latest = financials[-1]
    previous = financials[-2]
    avg_roe = mean(item.roe for item in financials)
    profit_cagr = _cagr(financials[0].net_profit, latest.net_profit, len(financials) - 1)
    revenue_cagr = _cagr(financials[0].revenue, latest.revenue, len(financials) - 1)
    pe_discount = (company.industry_pe - company.pe) / company.industry_pe if company.industry_pe else 0
    high_news = sum(1 for item in company.news if item["importance"] == "高")
    risk_penalty = sum({"低": 0.4, "中": 0.8, "高": 1.3}.get(item["level"], 0.8) for item in company.risks)

    items = [
        {
            "name": "商业模式",
            "score": _clamp(12 + len(company.business_model.get("moat", [])) * 1.4 + len(company.customers) * 0.5, 20),
            "max": 20,
            "reasons": [
                f"核心收入来自{', '.join(company.business_model.get('revenue_mix', {}).keys())}",
                f"护城河包括{', '.join(company.business_model.get('moat', []))}",
                f"主要客户覆盖{', '.join(company.customers)}",
            ],
        },
        {
            "name": "行业景气",
            "score": _clamp(8 + (4 if "AI" in company.concepts else 0) + (2 if "算力" in company.concepts else 0) + min(company.one_year_return / 25, 3), 15),
            "max": 15,
            "reasons": [
                f"所属概念包含{', '.join(company.concepts)}",
                f"最近一年涨跌幅为{company.one_year_return}%，反映市场景气预期",
                company.industry_analysis.get("growth", company.industry_analysis.get("position", "行业仍需持续跟踪")),
            ],
        },
        {
            "name": "盈利能力",
            "score": _clamp(7 + avg_roe / 2 + latest.net_margin / 3 + (2 if latest.net_profit > previous.net_profit else 0), 20),
            "max": 20,
            "reasons": [
                f"近五年平均ROE为{avg_roe:.1f}%",
                f"最新净利率为{latest.net_margin}%",
                f"最新净利润同比{'增长' if latest.net_profit > previous.net_profit else '下滑'}",
            ],
        },
        {
            "name": "成长能力",
            "score": _clamp(5 + profit_cagr * 45 + revenue_cagr * 25, 15),
            "max": 15,
            "reasons": [
                f"近五年净利润复合增长率约{profit_cagr * 100:.1f}%",
                f"近五年营收复合增长率约{revenue_cagr * 100:.1f}%",
                f"增长驱动包括{', '.join(company.business_model.get('growth_drivers', []))}",
            ],
        },
        {
            "name": "估值水平",
            "score": _clamp(5 + pe_discount * 8 + (2 if company.peg <= 1.2 else 0) - max(company.pe_percentile - 60, 0) / 20, 10),
            "max": 10,
            "reasons": [
                f"当前PE为{company.pe}，行业平均PE为{company.industry_pe}",
                f"PEG为{company.peg}",
                f"历史PE百分位为{company.pe_percentile}%",
            ],
        },
        {
            "name": "财务健康",
            "score": _clamp(4 + (3 if latest.free_cash_flow > 0 else 0) + (2 if latest.debt_ratio < 55 else 0) + min(latest.cash / latest.revenue * 4, 1.5), 10),
            "max": 10,
            "reasons": [
                f"自由现金流为{latest.free_cash_flow}亿元",
                f"资产负债率为{latest.debt_ratio}%",
                f"现金储备为{latest.cash}亿元",
            ],
        },
        {
            "name": "风险控制",
            "score": _clamp(5 - risk_penalty, 5),
            "max": 5,
            "reasons": [
                f"识别到{len(company.risks)}项主要风险",
                f"风险等级为{company.risk_level}",
                "分数会随高等级风险数量增加而下降",
            ],
        },
        {
            "name": "消息面",
            "score": _clamp(2 + high_news * 1.2 + min(len(company.news), 3) * 0.6, 5),
            "max": 5,
            "reasons": [
                f"最近30天收录{len(company.news)}条重要消息",
                f"其中高重要性消息{high_news}条",
                "按公告、新闻和调研的重要程度综合打分",
            ],
        },
    ]
    total = sum(item["score"] for item in items)
    if total >= 85:
        verdict = "基本面优秀，行业景气度高，盈利质量较强，适合列入重点研究池。"
    elif total >= 75:
        verdict = "基本面较好，但估值、风险或增长确定性仍需进一步验证。"
    else:
        verdict = "存在明显短板，建议先确认盈利质量、行业景气和风险暴露。"
    return {"total": total, "items": items, "verdict": verdict}


def serialize_company(company: Company) -> dict:
    result = asdict(company)
    result["financials"] = [asdict(item) for item in company.financials]
    result["score"] = score_company(company)
    return result
