from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialYear:
    year: int
    revenue: float
    net_profit: float
    gross_margin: float
    net_margin: float
    roe: float
    roa: float
    eps: float
    free_cash_flow: float
    debt_ratio: float
    rd_expense: float
    cash: float


@dataclass(frozen=True)
class Company:
    code: str
    name: str
    industry: str
    market_cap: float
    pe: float
    pb: float
    peg: float
    ev_ebitda: float
    pe_percentile: int
    pb_percentile: int
    industry_pe: float
    one_year_return: float
    risk_level: str
    sectors: list[str]
    concepts: list[str]
    description: str
    products: list[str]
    customers: list[str]
    business_model: dict[str, str | list[str] | dict[str, int]]
    financials: list[FinancialYear]
    risks: list[dict[str, str]]
    news: list[dict[str, str]]
    shareholders: list[dict[str, str]]
    dividend: dict[str, float | int | str]
    industry_analysis: dict[str, str]
    peers: list[str]
    is_placeholder: bool = False


def _financials(
    revenues: list[float],
    profits: list[float],
    gross_margin: float,
    net_margin: float,
    roe: float,
    debt_ratio: float,
    rd_ratio: float,
    cash_ratio: float,
) -> list[FinancialYear]:
    years = [2021, 2022, 2023, 2024, 2025]
    rows = []
    for index, year in enumerate(years):
        revenue = revenues[index]
        profit = profits[index]
        rows.append(
            FinancialYear(
                year=year,
                revenue=revenue,
                net_profit=profit,
                gross_margin=round(gross_margin + index * 0.35, 1),
                net_margin=round(net_margin + index * 0.2, 1),
                roe=round(roe + index * 0.55, 1),
                roa=round((roe + index * 0.55) / 2.1, 1),
                eps=round(profit / 190, 2),
                free_cash_flow=round(profit * 0.86, 1),
                debt_ratio=round(debt_ratio - index * 0.7, 1),
                rd_expense=round(revenue * rd_ratio, 1),
                cash=round(revenue * cash_ratio, 1),
            )
        )
    return rows


def _company(
    code: str,
    name: str,
    industry: str,
    market_cap: float,
    pe: float,
    pb: float,
    one_year_return: float,
    sectors: list[str],
    description: str,
    products: list[str],
    customers: list[str],
    revenue_mix: dict[str, int],
    growth_drivers: list[str],
    moat: list[str],
    financials: list[FinancialYear],
    risks: list[dict[str, str]],
    peers: list[str],
    risk_level: str = "中",
    peg: float = 1.2,
    industry_pe: float = 28.0,
    concepts: list[str] | None = None,
) -> Company:
    return Company(
        code=code,
        name=name,
        industry=industry,
        market_cap=market_cap,
        pe=pe,
        pb=pb,
        peg=peg,
        ev_ebitda=round(pe * 0.65, 1),
        pe_percentile=min(90, max(10, round(pe / max(industry_pe, 1) * 55))),
        pb_percentile=min(90, max(10, round(pb * 12))),
        industry_pe=industry_pe,
        one_year_return=one_year_return,
        risk_level=risk_level,
        sectors=sectors,
        concepts=concepts or sectors[:4],
        description=description,
        products=products,
        customers=customers,
        business_model={
            "summary": f"{name}主要通过{', '.join(revenue_mix.keys())}获得收入，增长重点来自{', '.join(growth_drivers[:2])}。",
            "revenue_mix": revenue_mix,
            "growth_drivers": growth_drivers,
            "moat": moat,
        },
        financials=financials,
        risks=risks,
        news=[
            {"date": "2026-06-26", "importance": "高", "title": f"{name}近期经营数据受到关注", "summary": f"市场重点关注{name}的订单、盈利质量和行业景气变化。"},
            {"date": "2026-06-15", "importance": "中", "title": "机构调研聚焦业务增长点", "summary": f"投资者主要询问{', '.join(growth_drivers[:2])}。"},
            {"date": "2026-06-03", "importance": "中", "title": "行业景气变化影响估值", "summary": f"{industry}板块估值和盈利预期出现分化。"},
        ],
        shareholders=[
            {"name": "控股股东", "change": "稳定", "detail": "控股股东持股结构整体稳定。"},
            {"name": "机构资金", "change": "跟踪", "detail": "机构持仓变化需要结合季报继续观察。"},
        ],
        dividend={"total": round(financials[-1].net_profit * 1.2, 1), "yield": 1.6, "payout_ratio": 30.0, "years": 5, "score": "良好"},
        industry_analysis={
            "size": f"{industry}行业空间取决于终端需求、资本开支和政策周期。",
            "growth": f"{industry}的增长来自需求升级、国产替代和龙头集中度提升。",
            "competition": "行业竞争核心是技术、渠道、成本、品牌和交付能力。",
            "position": f"{name}属于{industry}领域的重要上市公司。",
        },
        peers=peers,
    )


COMPANIES: dict[str, Company] = {
    "601138": _company(
        "601138",
        "工业富联",
        "电子制造",
        4680,
        24.8,
        4.4,
        42.6,
        ["AI服务器", "算力", "消费电子", "机器人", "苹果产业链", "数据中心"],
        "公司是全球领先的电子制造与云端设备服务商，核心业务覆盖通信网络设备、云计算服务器、精密机构件和工业互联网服务。",
        ["AI服务器", "云服务器", "网络通信设备", "精密结构件"],
        ["全球云厂商", "通信设备商", "消费电子品牌客户"],
        {"云计算": 48, "通信网络": 34, "精密机构件": 13, "工业互联网": 5},
        ["AI服务器渗透率提升", "海外云厂商资本开支扩张", "工业互联网方案复用"],
        ["全球化交付能力", "大客户认证壁垒", "供应链效率", "服务器整机集成经验"],
        _financials([4395, 5118, 4763, 5184, 5930], [200, 201, 210, 242, 289], 8.3, 4.6, 18.1, 52.4, 0.026, 0.20),
        [
            {"name": "客户集中风险", "level": "中", "detail": "收入依赖头部云厂商和消费电子客户，客户资本开支变化会放大订单波动。"},
            {"name": "毛利率风险", "level": "中", "detail": "制造业务毛利率绝对水平不高，需要靠产品结构和良率改善维持盈利。"},
        ],
        ["000977", "300308", "300502"],
        industry_pe=32.5,
        concepts=["AI", "算力", "服务器", "云计算", "高端制造"],
    ),
    "000977": _company(
        "000977",
        "浪潮信息",
        "服务器",
        980,
        31.2,
        3.6,
        18.4,
        ["AI服务器", "算力", "数据中心"],
        "公司是服务器和IT基础设施供应商，受益于AI算力和数据中心建设。",
        ["通用服务器", "AI服务器", "存储系统"],
        ["互联网客户", "运营商", "政企客户"],
        {"服务器": 74, "存储": 12, "解决方案": 14},
        ["AI服务器需求", "政企数字化", "国产化替代"],
        ["品牌渠道", "服务器产品线", "行业客户基础"],
        _financials([670, 695, 658, 742, 856], [20, 21, 18, 23, 31], 11.4, 3.0, 13.0, 61.0, 0.055, 0.31),
        [{"name": "供应链风险", "level": "中", "detail": "上游核心芯片供应节奏影响交付和利润率。"}],
        ["601138", "300308", "300502"],
        industry_pe=32.5,
    ),
    "300308": _company(
        "300308",
        "中际旭创",
        "光模块",
        1760,
        38.5,
        8.9,
        55.3,
        ["光模块", "算力", "AI", "数据中心"],
        "公司是高速光模块供应商，受益于AI数据中心网络升级。",
        ["400G光模块", "800G光模块", "1.6T光模块"],
        ["海外云厂商", "设备商"],
        {"高速光模块": 88, "其他": 12},
        ["800G/1.6T升级", "AI集群网络扩容"],
        ["高速产品量产能力", "头部客户认证", "技术迭代速度"],
        _financials([77, 96, 107, 184, 263], [9, 12, 22, 46, 73], 25.6, 11.8, 13.8, 31.0, 0.10, 0.55),
        [{"name": "估值波动风险", "level": "中", "detail": "市场对AI光模块预期高，订单或毛利低于预期会引发估值回撤。"}],
        ["601138", "000977", "300502"],
        industry_pe=42.0,
    ),
    "300502": _company(
        "300502",
        "新易盛",
        "光模块",
        940,
        34.1,
        7.4,
        61.8,
        ["光模块", "算力", "AI", "数据中心"],
        "公司是高速光模块供应商，受益于AI网络高速互联需求。",
        ["高速光模块", "光器件"],
        ["云厂商", "通信设备商"],
        {"高速光模块": 82, "光器件": 18},
        ["AI网络升级", "高速率产品占比提升"],
        ["研发响应", "产品成本控制", "客户导入"],
        _financials([29, 33, 41, 71, 112], [6, 7, 9, 19, 34], 31.1, 20.3, 18.6, 22.1, 0.11, 0.76),
        [{"name": "客户和产品迭代风险", "level": "中", "detail": "高速光模块迭代快，客户导入节奏影响增长确定性。"}],
        ["601138", "000977", "300308"],
        industry_pe=42.0,
    ),
    "600519": _company(
        "600519",
        "贵州茅台",
        "白酒",
        19800,
        26.5,
        8.5,
        7.2,
        ["白酒", "消费", "高端品牌", "红利"],
        "公司是高端白酒龙头，核心产品具备强品牌力和渠道议价能力。",
        ["飞天茅台", "系列酒"],
        ["经销商", "直营渠道", "企业和个人消费者"],
        {"茅台酒": 85, "系列酒": 12, "其他": 3},
        ["直营占比提升", "品牌稀缺性", "产品结构升级"],
        ["品牌心智", "渠道控制", "稀缺产能", "现金流能力"],
        _financials([1095, 1276, 1505, 1739, 1986], [525, 627, 747, 862, 994], 91.5, 48.0, 30.0, 19.0, 0.015, 0.45),
        [{"name": "消费需求风险", "level": "中", "detail": "高端白酒需求受商务消费、居民收入和渠道库存影响。"}],
        ["000858", "000568", "603369"],
        industry_pe=24.0,
        concepts=["白酒", "消费", "红利"],
    ),
    "300750": _company(
        "300750",
        "宁德时代",
        "动力电池",
        7800,
        22.0,
        4.8,
        12.5,
        ["新能源", "动力电池", "储能", "锂电池"],
        "公司是全球动力电池龙头，业务覆盖动力电池、储能电池和电池材料体系。",
        ["动力电池", "储能系统", "电池材料"],
        ["新能源车企", "储能客户", "海外车企"],
        {"动力电池": 68, "储能": 19, "材料及其他": 13},
        ["储能增长", "海外客户拓展", "新技术平台"],
        ["规模成本", "技术研发", "客户绑定", "供应链管理"],
        _financials([1304, 3286, 4009, 4550, 5150], [159, 307, 441, 518, 610], 26.2, 12.2, 20.1, 67.0, 0.07, 0.22),
        [{"name": "价格竞争风险", "level": "中", "detail": "动力电池行业价格竞争会压缩毛利率。"}],
        ["002594", "002812", "300014"],
        industry_pe=26.0,
    ),
    "002594": _company(
        "002594",
        "比亚迪",
        "新能源车",
        7600,
        20.8,
        4.3,
        15.6,
        ["新能源车", "动力电池", "汽车", "出海"],
        "公司业务覆盖新能源汽车、动力电池和电子制造，垂直整合能力突出。",
        ["新能源汽车", "动力电池", "电子部件"],
        ["个人消费者", "海外经销商", "电子客户"],
        {"汽车": 79, "手机部件": 15, "电池": 6},
        ["海外销量提升", "高端车型放量", "电池技术迭代"],
        ["垂直整合", "规模制造", "渠道网络", "技术平台"],
        _financials([2161, 4241, 6023, 7350, 8420], [30, 166, 300, 395, 486], 13.0, 5.6, 13.5, 71.0, 0.045, 0.18),
        [{"name": "竞争加剧风险", "level": "中", "detail": "新能源车价格竞争和车型周期会影响利润弹性。"}],
        ["300750", "601633", "600104"],
        industry_pe=24.0,
    ),
    "688981": _company(
        "688981",
        "中芯国际",
        "半导体",
        5200,
        48.0,
        2.8,
        20.1,
        ["半导体", "晶圆代工", "国产替代"],
        "公司是国内领先晶圆代工企业，受益于半导体国产化和成熟制程需求。",
        ["晶圆代工", "特色工艺"],
        ["芯片设计公司", "电子终端客户"],
        {"晶圆代工": 95, "其他": 5},
        ["国产替代", "产能利用率改善", "特色工艺需求"],
        ["制造工艺", "产能规模", "客户基础"],
        _financials([356, 496, 452, 520, 610], [107, 121, 48, 62, 80], 27.0, 12.5, 8.0, 38.0, 0.14, 0.40),
        [{"name": "周期风险", "level": "中", "detail": "晶圆代工景气受库存周期和终端需求影响。"}],
        ["603986", "688012", "002371"],
        peg=1.8,
        industry_pe=45.0,
    ),
    "600036": _company(
        "600036",
        "招商银行",
        "银行",
        8900,
        7.2,
        1.0,
        4.1,
        ["银行", "金融", "红利", "财富管理"],
        "公司是零售银行龙头，核心优势来自客户基础、财富管理和资产质量。",
        ["公司贷款", "零售贷款", "财富管理", "信用卡"],
        ["个人客户", "企业客户", "高净值客户"],
        {"利息净收入": 62, "手续费": 24, "其他": 14},
        ["财富管理修复", "资产质量稳定", "零售客户经营"],
        ["零售客群", "风控体系", "品牌渠道", "低成本负债"],
        _financials([3313, 3448, 3391, 3570, 3725], [1199, 1380, 1466, 1535, 1610], 0.0, 42.0, 15.8, 91.0, 0.012, 0.08),
        [{"name": "净息差下行风险", "level": "中", "detail": "利率环境和资产收益率下行会压缩银行净息差。"}],
        ["601166", "000001", "601398"],
        industry_pe=6.5,
    ),
    "601318": _company(
        "601318",
        "中国平安",
        "保险",
        7300,
        8.9,
        0.9,
        6.8,
        ["保险", "金融", "红利", "大消费"],
        "公司是综合金融集团，寿险、财险、银行和投资业务共同贡献利润。",
        ["寿险", "财险", "银行", "资产管理"],
        ["个人客户", "企业客户"],
        {"寿险": 46, "财险": 27, "银行": 21, "其他": 6},
        ["寿险改革", "投资收益改善", "综合金融协同"],
        ["客户规模", "代理人体系", "综合金融牌照"],
        _financials([11804, 11105, 10366, 11020, 11680], [1016, 837, 856, 965, 1080], 0.0, 9.2, 10.5, 88.0, 0.01, 0.10),
        [{"name": "投资收益波动风险", "level": "中", "detail": "资本市场波动会影响保险投资收益和内含价值。"}],
        ["601628", "601601", "601336"],
        industry_pe=9.5,
    ),
    "300059": _company(
        "300059",
        "东方财富",
        "证券",
        3100,
        31.0,
        4.2,
        19.9,
        ["证券", "互联网金融", "基金销售"],
        "公司以互联网金融平台为基础，业务覆盖证券经纪、两融和基金销售。",
        ["证券经纪", "基金销售", "金融数据服务"],
        ["个人投资者", "基金公司", "机构客户"],
        {"证券服务": 58, "基金销售": 26, "金融数据": 16},
        ["市场活跃度提升", "基金销售恢复", "平台用户变现"],
        ["用户流量", "低成本获客", "牌照协同"],
        _financials([130, 124, 110, 132, 158], [86, 85, 82, 95, 116], 63.0, 66.0, 17.5, 32.0, 0.08, 1.1),
        [{"name": "市场成交低迷风险", "level": "中", "detail": "成交额和基金发行低迷会影响经纪及代销收入。"}],
        ["600030", "601688", "601211"],
        industry_pe=27.0,
    ),
    "002230": _company(
        "002230",
        "科大讯飞",
        "人工智能",
        1050,
        58.0,
        5.1,
        26.2,
        ["AI", "大模型", "教育信息化", "语音识别"],
        "公司长期深耕智能语音和人工智能，业务覆盖教育、办公、医疗和开放平台。",
        ["AI学习机", "语音识别", "行业AI方案", "大模型服务"],
        ["教育客户", "政企客户", "个人消费者"],
        {"教育产品": 36, "开放平台": 22, "政企AI": 30, "其他": 12},
        ["大模型商业化", "教育硬件放量", "行业AI应用"],
        ["语音技术", "数据积累", "渠道场景", "品牌认知"],
        _financials([183, 188, 196, 226, 272], [16, 6, 7, 12, 19], 40.0, 6.0, 5.8, 43.0, 0.22, 0.33),
        [{"name": "商业化不确定风险", "level": "中", "detail": "AI投入大，商业化节奏会影响利润释放。"}],
        ["688111", "300496", "300033"],
        peg=2.1,
        industry_pe=50.0,
    ),
    "002475": _company(
        "002475",
        "立讯精密",
        "消费电子",
        3050,
        23.6,
        4.0,
        14.3,
        ["消费电子", "苹果产业链", "汽车电子", "AI硬件"],
        "公司是消费电子精密制造龙头，并向汽车电子、通信和AI硬件延伸。",
        ["连接器", "声学模组", "整机组装", "汽车电子"],
        ["消费电子品牌客户", "汽车客户", "通信客户"],
        {"消费电子": 78, "通信": 9, "汽车电子": 8, "其他": 5},
        ["AI硬件创新", "汽车电子扩张", "大客户份额提升"],
        ["精密制造", "大客户配套", "供应链效率", "多品类扩张"],
        _financials([1539, 2140, 2319, 2550, 2910], [70, 92, 110, 132, 162], 12.0, 5.0, 17.0, 57.0, 0.045, 0.18),
        [{"name": "大客户依赖风险", "level": "中", "detail": "消费电子大客户订单变化会影响收入和产能利用率。"}],
        ["601138", "002241", "300433"],
        industry_pe=28.0,
    ),
    "605358": _company(
        "605358",
        "立昂微",
        "半导体",
        210,
        62.0,
        2.4,
        -8.5,
        ["半导体", "硅片", "功率器件", "国产替代"],
        "公司主要从事半导体硅片、分立器件芯片和功率器件业务，受半导体周期、产能利用率和国产替代节奏影响较大。",
        ["半导体硅片", "分立器件芯片", "功率器件"],
        ["晶圆厂", "功率器件客户", "电子制造客户"],
        {"半导体硅片": 46, "分立器件芯片": 32, "功率器件": 22},
        ["半导体国产替代", "产能利用率修复", "功率器件需求恢复"],
        ["硅片制造经验", "客户认证", "多业务协同"],
        _financials([25, 29, 27, 31, 36], [6.0, 6.9, 3.8, 4.6, 5.8], 35.0, 14.0, 8.0, 42.0, 0.10, 0.30),
        [
            {"name": "半导体周期风险", "level": "中", "detail": "硅片和功率器件需求受下游库存周期影响，产能利用率变化会放大利润波动。"},
            {"name": "资本开支风险", "level": "中", "detail": "半导体制造资产较重，扩产节奏和折旧压力会影响盈利释放。"},
        ],
        ["688981", "603986", "688012"],
        peg=2.0,
        industry_pe=45.0,
        concepts=["半导体", "硅片", "功率器件", "国产替代"],
    ),
}

ALIASES = {
    "茅台": "600519",
    "宁王": "300750",
    "比亚迪股份": "002594",
    "招行": "600036",
    "平安": "601318",
    "东财": "300059",
    "讯飞": "002230",
    "立讯": "002475",
    "立昂": "605358",
    "立昂微电子": "605358",
}

HOT_SECTORS = ["AI", "算力", "半导体", "新能源", "医药", "消费", "银行", "军工", "机器人", "光模块", "低空经济", "证券", "白酒"]


def all_companies() -> list[Company]:
    return list(COMPANIES.values())


def find_company(query: str) -> Company | None:
    normalized = query.strip().lower()
    if not normalized:
        return None
    if normalized in COMPANIES:
        return COMPANIES[normalized]
    if query.strip() in ALIASES:
        return COMPANIES[ALIASES[query.strip()]]
    for company in COMPANIES.values():
        if normalized in {company.code.lower(), company.name.lower()}:
            return company
    for company in COMPANIES.values():
        if normalized in company.name.lower() or normalized in company.code.lower():
            return company
    return None


def build_placeholder_company(query: str) -> Company:
    name = query.strip() or "未命名股票"
    code = name if name.isdigit() else "AI-SEARCH"
    return Company(
        code=code,
        name=name,
        industry="待识别",
        market_cap=0,
        pe=0,
        pb=0,
        peg=0,
        ev_ebitda=0,
        pe_percentile=50,
        pb_percentile=50,
        industry_pe=0,
        one_year_return=0,
        risk_level="待研究",
        sectors=["待AI搜索", "待接入数据源"],
        concepts=["待AI搜索"],
        description=f"当前样例库暂未收录“{name}”。页面已生成研究框架，下一步应接入搜索/公告/财报数据源后自动填充真实结论。",
        products=["待AI从公司资料中提取"],
        customers=["待AI从年报和公告中提取"],
        business_model={
            "summary": "该公司尚未进入本地研究库。可以通过AI搜索公司官网、年报、公告、新闻和研报摘要，提取主营业务、收入结构、客户、风险和同行。",
            "revenue_mix": {"待提取": 100},
            "growth_drivers": ["接入AI搜索后自动生成", "接入财报数据后自动计算", "接入新闻公告后自动排序"],
            "moat": ["待AI从资料中识别"],
        },
        financials=_financials([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 0, 0, 0, 0, 0, 0),
        risks=[{"name": "数据缺失风险", "level": "高", "detail": "该股票尚未接入真实数据，不能根据当前页面做投资判断。"}],
        news=[{"date": "2026-06-30", "importance": "高", "title": "等待AI研究任务", "summary": "需要接入搜索、财报、公告和新闻数据源后生成最近30天重大消息。"}],
        shareholders=[],
        dividend={"total": 0, "yield": 0, "payout_ratio": 0, "years": 0, "score": "待研究"},
        industry_analysis={"position": "待AI识别行业和同行。"},
        peers=[],
        is_placeholder=True,
    )


def build_dynamic_a_share_company(
    code: str,
    name: str,
    price: float | None = None,
    change_pct: float | None = None,
    market_cap: float | None = None,
    pe: float | None = None,
    pb: float | None = None,
) -> Company:
    return Company(
        code=code,
        name=name,
        industry="A股公司（待AI研究）",
        market_cap=market_cap or 0,
        pe=pe or 0,
        pb=pb or 0,
        peg=0,
        ev_ebitda=0,
        pe_percentile=50,
        pb_percentile=50,
        industry_pe=0,
        one_year_return=change_pct or 0,
        risk_level="待研究",
        sectors=["A股", "待AI搜索", "实时行情"],
        concepts=["A股", "待AI搜索"],
        description=f"{name}（{code}）已从A股实时股票池识别。当前已接入行情估值字段，财报、公告、新闻、研报和行业结论需要通过AI搜索任务继续补齐。",
        products=["已接入A股股票池", "已接入实时行情估值", "正在等待公告和财报解析"],
        customers=["公开市场投资者", "待AI从定期报告和公告提取"],
        business_model={
            "summary": "该公司已命中A股股票池，页面会自动触发AI自动研究，继续收集公告、行情估值和可用公开资料。",
            "revenue_mix": {"待财报解析": 100},
            "growth_drivers": ["自动搜索公司资料", "解析近五年财报", "整理最近公告新闻", "识别同行公司"],
            "moat": ["待从公告、年报和行业资料中识别"],
        },
        financials=_financials([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 0, 0, 0, 0, 0, 0),
        risks=[{"name": "研究数据缺失风险", "level": "高", "detail": "当前仅完成股票池和实时行情识别，基本面结论等待AI搜索和财报数据补齐。"}],
        news=[{"date": "2026-06-30", "importance": "高", "title": "等待AI研究任务", "summary": "已识别A股代码和名称，下一步应自动抓取公告、新闻、财报和同行资料。"}],
        shareholders=[],
        dividend={"total": 0, "yield": 0, "payout_ratio": 0, "years": 0, "score": "待研究"},
        industry_analysis={"position": "待AI识别行业、竞争格局和同行公司。"},
        peers=[],
        is_placeholder=True,
    )
