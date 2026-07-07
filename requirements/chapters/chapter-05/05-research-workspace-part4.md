# Chapter 05 --- Research Workspace (Part 4)

**Product Design Specification (PDS)**\
Version: v1.0

------------------------------------------------------------------------

# 21. API Contract

## GET /api/v1/workspace

### Purpose

获取 Workspace 首页所有聚合数据。

### Response

``` json
{
  "marketPulse": {},
  "dailyBrief": {},
  "researchQueue": [],
  "hotSectors": [],
  "watchlist": [],
  "riskAlerts": []
}
```

要求：

-   聚合接口，减少前端请求次数
-   支持局部刷新
-   返回时间 \< 500ms（缓存命中）

------------------------------------------------------------------------

## GET /api/v1/watchlist

返回用户观察池。

支持：

-   分页
-   排序
-   搜索
-   风险过滤

------------------------------------------------------------------------

## POST /api/v1/watchlist

添加股票进入观察池。

请求：

``` json
{
  "stockCode": "601138"
}
```

------------------------------------------------------------------------

## DELETE /api/v1/watchlist/{id}

移除观察池股票。

------------------------------------------------------------------------

# 22. State Machine

Workspace 状态：

``` text
Loading
   │
   ▼
Ready
   │
   ├────► Refreshing
   │           │
   │           ▼
   │         Ready
   │
   ├────► Empty
   │
   └────► Error
               │
               ▼
            Retry
```

原则：

-   每个模块独立维护状态
-   一个模块失败不影响其它模块
-   Retry 不刷新整个页面

------------------------------------------------------------------------

# 23. Error Recovery

统一错误处理：

  场景          UI
  ------------- ------------------
  网络超时      Retry 按钮
  AI 服务异常   展示上次成功结果
  数据为空      Empty State
  权限失效      跳转登录

日志：

记录：

-   requestId
-   userId
-   timestamp
-   module
-   errorCode

------------------------------------------------------------------------

# 24. Performance Requirements

首次加载：

\< 2 秒

局部刷新：

\< 300ms

AI Summary：

\< 5 秒

Watchlist：

支持 1000+ 股票

Research Queue：

支持无限分页。

------------------------------------------------------------------------

# 25. Telemetry

埋点：

-   打开 Workspace
-   点击板块
-   查看股票
-   加入观察池
-   删除观察池
-   AI 提问
-   AI 生成报告

指标：

-   Daily Active User
-   Daily Research Count
-   Watchlist Size
-   AI Usage
-   Average Research Time

------------------------------------------------------------------------

# 26. Security

原则：

-   所有接口鉴权
-   JWT Token
-   HTTPS
-   敏感字段脱敏
-   操作日志保留

AI：

不得生成：

-   买入建议
-   保证收益
-   虚假结论

所有分析必须可解释。

------------------------------------------------------------------------

# 27. Future Roadmap

V1

-   Workspace
-   Research Queue
-   Watchlist
-   AI Daily

V2

-   Portfolio
-   ETF
-   港股
-   美股

V3

-   Multi-Agent
-   Portfolio Review
-   Knowledge Graph
-   Personal Research Memory

------------------------------------------------------------------------

# 28. Chapter Summary

Research Workspace 是整个 AlphaLens 的核心入口。

它不是一个 Dashboard，而是用户每天开展研究工作的工作台。

Workspace 的使命：

-   告诉用户今天发生了什么；
-   告诉用户今天应该研究什么；
-   帮助用户持续跟踪；
-   帮助用户形成自己的投资研究体系。

------------------------------------------------------------------------

# Chapter 05 Completed

下一章：

Chapter 06 --- Design System

内容包括：

-   Color System
-   Typography
-   Layout Grid
-   Components
-   Card Design
-   Motion
-   Icons
-   Accessibility
-   Responsive Design
-   Design Tokens
