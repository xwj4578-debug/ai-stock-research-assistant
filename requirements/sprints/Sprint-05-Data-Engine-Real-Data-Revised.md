# Sprint 05 --- Data Engine & Real Market Data (Revised)

> **Revision:** Architecture Upgrade\
> **Status:** Replace previous Sprint 05 document

------------------------------------------------------------------------

# Architecture Upgrade

本 Sprint 的重点不是"接入 AKShare"。

真正目标是：

> **建立 AlphaLens Data Engine（数据引擎）基础架构。**

AKShare 只是第一种数据提供者（Provider），以后可以无缝替换。

------------------------------------------------------------------------

# Core Principle

数据源可以替换。

AI 可以替换。

前端可以升级。

**Research Engine 与 Data Engine 才是 AlphaLens 的核心资产。**

------------------------------------------------------------------------

# Recommended Architecture

``` text
Next.js Frontend
        │
REST API
        │
API Controller
        │
Application Service
        │
Research Engine (Domain)
        │
Repository
        │
Provider
        ├── AKShare
        ├── EastMoney
        ├── Tushare
        ├── Sina
        └── Mock
```

职责：

## API Controller

-   参数校验
-   返回统一 Response
-   不包含业务逻辑

## Application Service

负责组合业务流程，例如：

-   获取 Workspace 数据
-   聚合多个领域服务
-   返回页面模型

## Research Engine（Domain）

AlphaLens 的核心。

负责：

-   综合评分
-   板块热度
-   Research Queue 排序
-   Watchlist 优先级
-   风险计算
-   解释评分原因

注意：

> 不直接访问第三方数据。

## Repository

负责：

-   统一 Provider 返回格式
-   数据缓存
-   重试
-   降级
-   数据转换

Repository 对 Domain 提供稳定的数据模型。

## Provider

只负责调用外部数据源。

例如：

-   AKShare
-   东方财富
-   Tushare
-   新浪财经

Provider 不包含业务逻辑。

------------------------------------------------------------------------

# Backend Structure (Updated)

``` text
backend/
└── app/
    ├── api/
    ├── application/
    │   └── workspace_service.py
    ├── domain/
    │   ├── research_engine.py
    │   ├── scoring.py
    │   └── ranking.py
    ├── repository/
    │   ├── market_repository.py
    │   └── cache_repository.py
    ├── providers/
    │   ├── base.py
    │   ├── akshare_provider.py
    │   ├── eastmoney_provider.py
    │   └── mock_provider.py
    ├── schemas/
    ├── core/
    └── main.py
```

------------------------------------------------------------------------

# Provider Rules

所有 Provider 必须实现统一接口：

``` python
class MarketProvider:
    def get_market_overview(self): ...
    def get_hot_sectors(self): ...
    def get_market_news(self): ...
    def get_limit_statistics(self): ...
```

返回统一的数据结构。

------------------------------------------------------------------------

# Repository Rules

Repository 必须：

-   调用 Provider
-   数据标准化
-   Cache
-   Retry
-   Fallback

例如：

``` text
AKShare
   │
失败
   ▼
MockProvider
```

------------------------------------------------------------------------

# Research Engine Rules

Research Engine 不知道 AKShare。

Research Engine 只知道：

``` python
market = repository.get_market_overview()
```

然后完成：

-   综合评分
-   热点排序
-   风险计算
-   推荐研究顺序

------------------------------------------------------------------------

# Acceptance Criteria（新增）

除上一版要求外，还必须满足：

-   Provider 可替换
-   Repository 不依赖具体 Provider
-   Domain 不依赖第三方 SDK
-   前端无需关心数据来源
-   后续增加数据源无需修改业务逻辑

------------------------------------------------------------------------

# Updated Codex Tasks

新增要求：

1.  建立 Application / Domain / Repository 三层。
2.  Provider 仅负责第三方接口调用。
3.  Repository 负责缓存、重试、Fallback。
4.  Research Engine 不允许直接调用 Provider。
5.  Workspace API 只能调用 Application Service。
6.  所有模块保持低耦合，方便未来接入更多数据源。

------------------------------------------------------------------------

# Why This Architecture

这样设计后：

-   更换 AKShare → 东方财富，不影响前端。
-   引入 Redis 缓存，只修改 Repository。
-   增加港股、美股 Provider，不影响 Domain。
-   增加 AI Engine，不影响数据层。

最终形成：

**UI Layer → Application → Research Engine → Repository → Provider**

这是 AlphaLens 后续所有能力的基础。
