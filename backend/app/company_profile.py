from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen


def _clean_text(value: Any, max_len: int | None = None) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if max_len and len(text) > max_len:
        return text[:max_len].rstrip() + "..."
    return text


def _split_concepts(value: str, limit: int = 8) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()][:limit]


def _infer_products(main_business: str, business_scope: str) -> list[str]:
    text = main_business or business_scope
    candidates = []
    rules = [
        ("封装测试服务", ["封装", "测试"]),
        ("晶圆级芯片尺寸封装", ["晶圆级", "芯片尺寸封装"]),
        ("集成电路产品", ["集成电路"]),
        ("传感器封装", ["传感器"]),
        ("功率器件", ["功率器件"]),
        ("半导体硅片", ["硅片"]),
        ("软件和信息服务", ["软件", "信息"]),
        ("银行金融服务", ["银行", "贷款", "存款"]),
    ]
    for name, keywords in rules:
        if all(keyword in text for keyword in keywords):
            candidates.append(name)
    if candidates:
        return candidates[:4]
    if main_business:
        return [_clean_text(main_business, 42)]
    return ["待从年报分部收入中进一步拆分"]


def _infer_customers(profile: str, industry: str, concepts: list[str]) -> list[str]:
    text = profile + " " + industry + " " + " ".join(concepts)
    if "半导体" in text or "芯片" in text or "封装" in text:
        return ["芯片设计公司", "传感器厂商", "电子终端客户"]
    if "银行" in text:
        return ["个人客户", "企业客户", "同业金融机构"]
    if "石油" in text or "天然气" in text:
        return ["成品油和化工客户", "天然气用户", "工业企业"]
    if "房地产" in text:
        return ["购房客户", "商业地产租户", "物业服务客户"]
    return ["待从年报客户结构中进一步识别"]


def infer_growth_drivers(main_business: str, industry: str, concepts: list[str]) -> list[str]:
    text = main_business + " " + industry + " " + " ".join(concepts)
    drivers = []
    if "先进封装" in text or "封装" in text:
        drivers.append("先进封装需求提升")
    if "传感器" in text or "摄像头" in text or "生物识别" in text:
        drivers.append("传感器和成像应用扩张")
    if "国产芯片" in text or "半导体" in text:
        drivers.append("半导体国产替代")
    if "汽车芯片" in text:
        drivers.append("汽车电子需求增长")
    if "5G" in text or "通信" in text:
        drivers.append("通信和终端设备升级")
    return drivers[:4] or ["增长点待结合年报、公告和行业资料验证"]


def infer_moat(main_business: str, profile: str, concepts: list[str]) -> list[str]:
    text = main_business + " " + profile + " " + " ".join(concepts)
    moats = []
    if "技术引领" in text or "技术创新" in text or "先进封装" in text:
        moats.append("封装技术和工艺积累")
    if "量产" in text or "规模量产" in text:
        moats.append("规模量产和交付能力")
    if "客户" in text:
        moats.append("客户认证和服务经验")
    if "12英寸" in text or "8英寸" in text:
        moats.append("8英寸/12英寸产线能力")
    return moats[:4] or ["护城河待结合客户、专利和产能资料验证"]


def fetch_company_profile(code: str) -> dict[str, Any] | None:
    if not code.isdigit() or len(code) != 6:
        return None
    filter_expr = quote(f'(SECURITY_CODE="{code}")', safe="()=")
    url = (
        "https://datacenter-web.eastmoney.com/api/data/v1/get"
        "?reportName=RPT_F10_ORG_BASICINFO"
        "&columns=ALL"
        f"&filter={filter_expr}"
        "&pageNumber=1&pageSize=1"
    )
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    rows = (payload.get("result") or {}).get("data") or []
    if not rows:
        return None
    row = rows[0]
    main_business = _clean_text(row.get("MAIN_BUSINESS"))
    business_scope = _clean_text(row.get("BUSINESS_SCOPE"))
    profile = _clean_text(row.get("ORG_PROFIE"), 420)
    industry = _clean_text(row.get("EM2016"))
    concepts = _split_concepts(str(row.get("BLGAINIAN") or ""))
    products = _infer_products(main_business, business_scope)
    customers = _infer_customers(profile + " " + main_business, industry, concepts)
    growth_drivers = infer_growth_drivers(main_business, industry, concepts)
    moat = infer_moat(main_business, profile, concepts)
    return {
        "name": _clean_text(row.get("SECURITY_NAME_ABBR")),
        "full_name": _clean_text(row.get("ORG_NAME")),
        "industry": industry,
        "concepts": concepts,
        "description": profile or main_business or business_scope,
        "main_business": main_business,
        "business_scope": business_scope,
        "products": products,
        "customers": customers,
        "growth_drivers": growth_drivers,
        "moat": moat,
        "business_summary": main_business or business_scope or "主营业务待进一步解析。",
        "source": "东方财富F10公司资料",
    }
