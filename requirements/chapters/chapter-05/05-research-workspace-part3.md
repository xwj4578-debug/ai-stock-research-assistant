# Chapter 05 --- Research Workspace (Part 3)

**Product Design Specification (PDS)**\
Version: v1.0

------------------------------------------------------------------------

# 15. Workspace Interaction Flow

## Research Workflow

``` text
进入 Workspace
        │
        ▼
查看 Market Pulse
        │
        ▼
阅读 AI Daily Brief
        │
        ▼
选择 Hot Sector
        │
        ▼
查看板块详情
        │
        ▼
选择目标股票
        │
        ▼
阅读 AI Research Report
        │
        ▼
加入 Watchlist
        │
        ▼
持续跟踪
        │
        ▼
触发买点 / 放弃研究
```

设计原则：

-   每一步都有明确目标
-   不允许出现"下一步不知道做什么"
-   AI 始终给出下一步建议

------------------------------------------------------------------------

# 16. Component Specification

## Market Pulse Card

作用：

展示市场整体状态。

交互：

-   点击进入 Market 页面
-   Hover 展示详细指标
-   AI 总结可展开

刷新：

每 60 秒自动刷新。

------------------------------------------------------------------------

## Research Queue Card

作用：

今天必须完成的研究任务。

交互：

-   点击进入股票详情
-   拖拽调整优先级（后续版本）
-   标记完成
-   移除任务

AI 自动排序：

1.  风险
2.  买点
3.  热度
4.  用户偏好

------------------------------------------------------------------------

## Watchlist Card

支持：

-   Pin
-   删除
-   设置提醒
-   查看变化记录

颜色：

绿色：评分提升

黄色：无变化

红色：风险增加

------------------------------------------------------------------------

## AI Copilot Panel

默认位于右侧。

支持：

-   可收起
-   可拖拽宽度
-   保留上下文
-   引用当前股票
-   引用当前板块

快捷按钮：

-   为什么上涨？
-   为什么下跌？
-   风险有哪些？
-   对比同行
-   生成报告

------------------------------------------------------------------------

# 17. Database Design (Draft)

## workspace_snapshot

  字段           类型        说明
  -------------- ----------- ----------
  id             uuid        主键
  user_id        uuid        用户
  market_score   int         市场评分
  summary        text        AI 日报
  created_at     timestamp   时间

------------------------------------------------------------------------

## research_queue

  字段         类型
  ------------ -----------
  id           uuid
  stock_code   varchar
  priority     int
  status       varchar
  ai_reason    text
  updated_at   timestamp

状态：

-   pending
-   researching
-   completed
-   archived

------------------------------------------------------------------------

## watchlist

  字段            类型
  --------------- -----------
  id              uuid
  stock_code      varchar
  score           int
  risk_level      varchar
  next_action     varchar
  last_analysis   timestamp

------------------------------------------------------------------------

# 18. AI Prompt Design

## Workspace Summary Prompt

目标：

生成首页 AI Daily Brief。

输入：

-   市场数据
-   板块数据
-   新闻
-   公告
-   资金流
-   用户观察池

输出：

1.  今日市场总结
2.  今日热点
3.  今日风险
4.  今日建议
5.  下一步研究任务

限制：

-   不超过 300 字
-   不直接推荐买卖
-   必须引用事实

------------------------------------------------------------------------

# 19. Codex Tasks

## Frontend

-   Workspace 页面框架
-   Sidebar
-   Market Pulse
-   Research Queue
-   Watchlist
-   AI Copilot 面板

## Backend

-   Workspace API
-   Queue API
-   Watchlist API

## Database

-   创建三张基础表
-   建立索引
-   初始化迁移

## AI

-   Workspace Summary Prompt
-   Queue Ranking Logic

------------------------------------------------------------------------

# 20. Acceptance Criteria

必须满足：

-   用户 30 秒内完成当天研究入口选择
-   页面首次加载 \< 2 秒（缓存命中）
-   AI 摘要可解释
-   各模块支持独立刷新
-   Watchlist 与 Research Queue 数据一致

------------------------------------------------------------------------

# Part 3 End

Next (Part 4):

-   Detailed API Contract
-   State Machine
-   Error Recovery
-   Performance Requirements
-   Telemetry & Analytics
-   Security
-   Future Roadmap
