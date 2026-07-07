from __future__ import annotations

from pathlib import Path
from dataclasses import replace

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .company_profile import fetch_company_profile
from .data import COMPANIES, HOT_SECTORS, all_companies, build_dynamic_a_share_company, build_placeholder_company, find_company
from .financials import fetch_financial_years
from .insights import fair_value_range, quality_value_scores, risk_level, score_color, valuation_gap, valuation_label
from .live_market import fetch_live_quote
from .market import analyze_target, market_overview, resolve_market_target
from .research import build_research_report
from .radar import build_market_radar
from .scoring import score_company, serialize_company
from .stock_universe import find_a_share, find_a_share_in_text, search_a_shares
from .stock_analysis import analyze_position, analyze_stock, compare_stocks, search_stock
from .workspace import (
    add_watchlist_item,
    build_workspace,
    build_workspace_v1,
    copilot_metadata,
    copilot_reply,
    list_watchlist,
    queue_action,
    telemetry_event,
)

BASE_DIR = Path(__file__).resolve().parents[2]
PROTOTYPE_DIR = BASE_DIR / "prototype" / "static"

app = FastAPI(title="AI 股票研究助手", version="0.2.0")
app.mount("/static", StaticFiles(directory=PROTOTYPE_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(PROTOTYPE_DIR / "index.html", media_type="text/html")


@app.get("/compare")
def compare_page() -> FileResponse:
    return FileResponse(PROTOTYPE_DIR / "index.html", media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/companies")
def companies(
    q: str = "",
    industry: str = "",
    concept: str = "",
    sort: str = Query("score", pattern="^(score|pe|roe|return)$"),
) -> list[dict]:
    rows = []
    for company in all_companies():
        latest = company.financials[-1]
        score = score_company(company)
        if q and q.lower() not in company.name.lower() and q not in company.code:
            continue
        if industry and industry != company.industry:
            continue
        if concept and concept not in company.concepts and concept not in company.sectors:
            continue
        rows.append(
            {
                "code": company.code,
                "name": company.name,
                "industry": company.industry,
                "market_cap": company.market_cap,
                "pe": company.pe,
                "pb": company.pb,
                "roe": latest.roe,
                "one_year_return": company.one_year_return,
                "risk_level": company.risk_level,
                "score": score["total"],
                "verdict": score["verdict"],
                "concepts": company.concepts,
            }
        )
    if q:
        known_codes = {row["code"] for row in rows}
        for listing in search_a_shares(q):
            if listing.code in known_codes:
                continue
            rows.append(
                {
                    "code": listing.code,
                    "name": listing.name,
                    "industry": "A股公司（待AI研究）",
                    "market_cap": listing.market_cap or 0,
                    "pe": listing.pe or 0,
                    "pb": listing.pb or 0,
                    "roe": 0,
                    "one_year_return": listing.change_pct or 0,
                    "risk_level": "待研究",
                    "score": 0,
                    "verdict": "已命中A股股票池，等待AI搜索补齐研究报告。",
                    "concepts": ["A股", "待AI搜索"],
                }
            )
    key_map = {"score": "score", "pe": "pe", "roe": "roe", "return": "one_year_return"}
    reverse = sort != "pe"
    return sorted(rows, key=lambda item: item[key_map[sort]], reverse=reverse)


@app.get("/api/companies/{query}")
def company_detail(query: str) -> dict:
    listing = find_a_share(query)
    company = None
    quote_for_code = None
    if listing:
        quote_for_code = fetch_live_quote(listing.code)
        company = build_dynamic_a_share_company(
            code=listing.code,
            name=(quote_for_code or {}).get("name") or listing.name,
            price=(quote_for_code or {}).get("price") or listing.price,
            change_pct=(quote_for_code or {}).get("change_pct") or listing.change_pct,
            market_cap=(quote_for_code or {}).get("market_cap") or listing.market_cap,
            pe=(quote_for_code or {}).get("pe") or listing.pe,
            pb=(quote_for_code or {}).get("pb") or listing.pb,
        )
    elif query.isdigit():
        quote_for_code = fetch_live_quote(query)
        if quote_for_code and quote_for_code.get("name"):
            company = build_dynamic_a_share_company(
                code=quote_for_code["code"],
                name=quote_for_code["name"],
                price=quote_for_code.get("price"),
                change_pct=quote_for_code.get("change_pct"),
                market_cap=quote_for_code.get("market_cap"),
                pe=quote_for_code.get("pe"),
                pb=quote_for_code.get("pb"),
            )
    if not company:
        company = build_placeholder_company(query)
    data = serialize_company(company)
    if company.is_placeholder:
        data["financials"] = []
        data["news"] = []
        data["products"] = []
        data["customers"] = []
        data["business_model"]["revenue_mix"] = {}
    live_quote = quote_for_code or (fetch_live_quote(company.code) if company.code.isdigit() else None)
    if not live_quote and listing:
        live_quote = {
            "code": listing.code,
            "name": listing.name,
            "price": listing.price,
            "market_cap": listing.market_cap,
            "pe": listing.pe,
            "pb": listing.pb,
            "change_pct": listing.change_pct,
            "source": "东方财富A股股票池",
            "updated_at": None,
        }
    if live_quote:
        for key in ("price", "change_pct", "pe", "pb", "market_cap"):
            if live_quote.get(key) is not None:
                data[key] = live_quote[key]
        data["live_quote"] = live_quote
    else:
        data["live_quote"] = {
            "source": "东方财富实时行情接口",
            "updated_at": None,
            "status": "实时行情暂不可用，未使用本地样例数据。",
        }
    if company.is_placeholder and company.code.isdigit():
        profile = fetch_company_profile(company.code)
        if profile:
            data["name"] = profile["name"] or data["name"]
            data["industry"] = profile["industry"] or data["industry"]
            data["description"] = profile["description"] or data["description"]
            data["products"] = profile["products"]
            data["customers"] = profile["customers"]
            data["sectors"] = profile["concepts"] or data["sectors"]
            data["concepts"] = profile["concepts"] or data["concepts"]
            data["business_model"]["summary"] = profile["business_summary"]
            data["business_model"]["revenue_mix"] = {"主营业务": 100}
            data["business_model"]["growth_drivers"] = profile["growth_drivers"]
            data["business_model"]["moat"] = profile["moat"]
            data["business_model"]["is_estimated"] = True
        financial_years = fetch_financial_years(company.code)
        if financial_years:
            data["financials"] = [
                {
                    "year": item.year,
                    "revenue": item.revenue,
                    "net_profit": item.net_profit,
                    "gross_margin": item.gross_margin,
                    "net_margin": item.net_margin,
                    "roe": item.roe,
                    "roa": item.roa,
                    "eps": item.eps,
                    "free_cash_flow": item.free_cash_flow,
                    "debt_ratio": item.debt_ratio,
                    "rd_expense": item.rd_expense,
                    "cash": item.cash,
                }
                for item in financial_years
            ]
            data["score"] = score_company(replace(company, financials=financial_years))
    financial_dicts = data.get("financials") or []
    latest_fin = financial_dicts[-1] if financial_dicts else {}
    previous_fin = financial_dicts[-2] if len(financial_dicts) >= 2 else {}
    profit_growth = (
        round((latest_fin["net_profit"] / previous_fin["net_profit"] - 1) * 100, 1)
        if latest_fin.get("net_profit") is not None and previous_fin.get("net_profit")
        else None
    )
    data["valuation_view"] = valuation_label(data.get("pe"), data.get("pb")) if company.is_placeholder else _valuation_view(company.pe_percentile, company.pb_percentile)
    current_price = data.get("price") or (data.get("live_quote") or {}).get("price")
    data["fair_value_range"] = fair_value_range(current_price, data.get("pe"), data.get("pb"))
    data["valuation_gap"] = valuation_gap(current_price, data["fair_value_range"])
    data["risk_level_dynamic"] = risk_level(data.get("pe"), data.get("pb"), latest_fin.get("debt_ratio"), profit_growth)
    data["score_color"] = score_color(data["score"]["total"])
    data["quality_scores"] = quality_value_scores(data["score"]["total"], data.get("pe"), data.get("pb"), latest_fin.get("roe"), profit_growth)
    if data.get("code") == "AI-SEARCH":
        data["ai_conclusion"] = "暂未识别到对应A股股票，请输入更准确的股票名称或6位代码。"
    else:
        data["ai_conclusion"] = (
            f"{data['name']}属于{data.get('industry') or 'A股'}，当前{data['valuation_view']}，风险等级{data['risk_level_dynamic']}，适合继续跟踪基本面变化。"
        )
    data["positioning"] = f"{data.get('industry') or 'A股'} / {'、'.join((data.get('concepts') or [])[:3])}"
    data["peers_detail"] = [
        {
            "code": peer.code,
            "name": peer.name,
            "revenue": peer.financials[-1].revenue,
            "net_profit": peer.financials[-1].net_profit,
            "roe": peer.financials[-1].roe,
            "pe": peer.pe,
            "pb": peer.pb,
            "growth": round((peer.financials[-1].net_profit / peer.financials[-2].net_profit - 1) * 100, 1) if peer.financials[-2].net_profit else 0,
            "gross_margin": peer.financials[-1].gross_margin,
            "rd_expense": peer.financials[-1].rd_expense,
            "score": score_company(peer)["total"],
        }
        for peer_code in company.peers
        if (peer := COMPANIES.get(peer_code))
    ]
    return data


@app.get("/api/live/quote/{code}")
def live_quote(code: str) -> dict:
    quote = fetch_live_quote(code)
    return quote or {"code": code, "status": "unavailable"}


@app.get("/api/stocks/search")
def stock_search_api(keyword: str = "", q: str = "", limit: int = Query(20, ge=1, le=50)) -> dict:
    query = keyword or q
    return {"items": search_stock(query, limit=limit)}


@app.get("/api/analyze/stock")
def analyze_stock_api(code: str = "", keyword: str = "") -> dict:
    return analyze_stock(code or keyword)


@app.post("/api/analyze/compare")
def analyze_compare_api(payload: dict) -> dict:
    stocks = payload.get("stocks") or []
    if isinstance(stocks, str):
        stocks = [item.strip() for item in stocks.replace("\n", ",").replace("，", ",").split(",") if item.strip()]
    return compare_stocks(stocks)


@app.post("/api/analyze/position")
def analyze_position_api(payload: dict) -> dict:
    return analyze_position(str(payload.get("code") or payload.get("stock") or ""), float(payload.get("cost")), payload.get("shares"))


@app.get("/api/research/{query}")
def research(query: str) -> dict:
    return build_research_report(query)


@app.get("/api/market/overview")
def market_api_overview() -> dict:
    return market_overview()


@app.get("/api/radar")
def market_radar_api() -> dict:
    return build_market_radar()


@app.get("/api/workspace")
def workspace_api() -> dict:
    return build_workspace()


@app.get("/api/v1/workspace")
def workspace_v1_api(module: str | None = None) -> dict:
    return build_workspace_v1(module=module)


@app.get("/api/workspace/copilot")
def workspace_copilot_api() -> dict:
    return copilot_metadata()


@app.post("/api/workspace/chat")
def workspace_chat_api(payload: dict) -> dict:
    return copilot_reply(payload)


@app.post("/api/watchlist")
def watchlist_add_api(payload: dict) -> dict:
    return add_watchlist_item(payload)


@app.delete("/api/watchlist/{item_id}")
def watchlist_delete_api(item_id: str) -> dict:
    return {"ok": True, "deleted": item_id}


@app.get("/api/v1/watchlist")
def watchlist_v1_api(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str = "",
    risk: str = "",
    sort: str = Query("score", pattern="^(score|risk|code)$"),
) -> dict:
    return list_watchlist(page=page, page_size=page_size, q=q, risk=risk, sort=sort)


@app.post("/api/v1/watchlist")
def watchlist_v1_add_api(payload: dict) -> dict:
    return add_watchlist_item(payload)


@app.delete("/api/v1/watchlist/{item_id}")
def watchlist_v1_delete_api(item_id: str) -> dict:
    return {"ok": True, "deleted": item_id}


@app.post("/api/v1/research-queue/{item_id}/{action}")
def research_queue_action_api(item_id: str, action: str) -> dict:
    return queue_action(item_id, action)


@app.post("/api/v1/telemetry")
def telemetry_api(payload: dict) -> dict:
    return telemetry_event(payload)


@app.get("/api/market/sector/{query}")
def market_api_sector(query: str) -> dict:
    return analyze_target(resolve_market_target(query))


@app.get("/api/sectors")
def sectors() -> dict:
    return {
        "hot": HOT_SECTORS,
        "industries": sorted({company.industry for company in all_companies()}),
        "concepts": sorted({concept for company in all_companies() for concept in company.concepts}),
    }


@app.get("/api/today")
def today_attention() -> list[dict]:
    items = []
    for company in all_companies():
        for news in company.news:
            if news["importance"] == "高":
                items.append({"company": company.name, "code": company.code, **news})
    return sorted(items, key=lambda item: item["date"], reverse=True)[:10]


@app.get("/api/ask")
def ask(q: str) -> dict:
    company = _company_from_question(q)
    score = score_company(company)
    lower = q.lower()
    if company.is_placeholder:
        report = build_research_report(company.code if company.code != "AI-SEARCH" else company.name)
        if "风险" in q:
            answer = f"{report['name']}的自动识别风险包括：" + "；".join(report["risks"][:4])
        elif "估值" in q or "低估" in q:
            valuation = report["valuation"]
            answer = f"{report['name']}估值初判为{valuation['label']}，PE为{valuation['pe']}，PB为{valuation['pb']}，总市值约{valuation['market_cap']}亿元。"
        else:
            answer = " ".join(report["summary"][:4])
    elif "风险" in q:
        answer = f"{company.name}的主要风险是：" + "；".join(f"{item['name']}：{item['detail']}" for item in company.risks)
    elif "roe" in lower or "20%" in q:
        qualified = [c.name for c in all_companies() if c.financials[-1].roe >= 20]
        answer = "最新ROE超过20%的样例公司包括：" + "、".join(qualified)
    elif "低估" in q or "估值" in q:
        answer = f"{company.name}当前PE为{company.pe}，行业均值为{company.industry_pe}，历史PE百分位{company.pe_percentile}%，系统判断为{_valuation_view(company.pe_percentile, company.pb_percentile)}。"
    else:
        answer = f"{company.name}综合评分{score['total']}分。{score['verdict']} 最近需要重点看盈利趋势、估值百分位、行业景气和关键风险。"
    return {"question": q, "answer": answer, "source": "本地样例研究库 + 动态A股自动研究接口。"}


def _company_from_question(question: str):
    for company in all_companies():
        if company.name in question or company.code in question:
            return company
    company = find_company(question)
    if company:
        return company
    listing = find_a_share(question)
    if not listing:
        listing = find_a_share_in_text(question)
    if listing:
        return build_dynamic_a_share_company(
            code=listing.code,
            name=listing.name,
            price=listing.price,
            change_pct=listing.change_pct,
            market_cap=listing.market_cap,
            pe=listing.pe,
            pb=listing.pb,
        )
    return build_placeholder_company(question)


def _valuation_view(pe_percentile: int, pb_percentile: int) -> str:
    avg = (pe_percentile + pb_percentile) / 2
    if avg < 30:
        return "低估"
    if avg < 60:
        return "合理"
    if avg < 80:
        return "偏高"
    return "高估"
