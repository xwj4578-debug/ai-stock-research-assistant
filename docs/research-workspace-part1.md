# Chapter 05 - Research Workspace (Part 1)

Product Design Specification v1.0

## 1. Overview

Research Workspace 是 AlphaLens 的核心页面。它不是传统意义上的首页，而是用户每天进入系统后的工作空间。

设计目标：

- 不直接推荐股票
- 不堆砌数据
- 帮助用户完成完整研究流程
- 所有信息围绕 Research Workflow 展开

## 2. 30 秒问题

Research Workspace 需要在 30 秒内回答：

1. 今天市场怎么样？
2. 今天哪些板块值得研究？
3. 哪几只股票值得继续研究？
4. 我的观察池有什么变化？
5. 今天有哪些风险？
6. 我下一步应该做什么？

## 3. Core Philosophy

Research > Decision

AI 的职责：

- 收集
- 整理
- 分析
- 总结
- 提醒

用户负责：

- 判断
- 决策
- 交易

## 4. Layout

```text
Logo / Search / AI / Notification / Profile
Sidebar / Main Workspace
Market Pulse
AI Daily Brief
Research Queue
Hot Sectors
Watchlist Changes
Risk Alerts
AI Copilot
```

## 5. Sidebar

固定导航：

- Workspace
- Market
- Sector
- Stocks
- Watchlist
- Research Reports
- Review
- Settings

规则：

- 一级导航不超过 8 个
- 支持键盘快捷键 1-8
- 当前模块高亮

## 6. Market Pulse

目标：用一屏展示市场状态。

字段：

- 市场情绪评分
- 两市成交额
- 上涨/下跌家数
- 涨停数
- 跌停数
- 炸板率
- 连板高度
- AI 一句话总结

## 7. AI Daily Brief

每天生成一份不超过 300 字的摘要。

包含：

- 今日市场概况
- 热点事件
- 热门板块
- 风险提示
- 今日研究建议

支持操作：

- 展开全文
- 一键生成长报告
- 导出 Markdown

## 8. Research Queue

Research Queue 是整个产品的核心。用户不需要每天重新找股票。

来源：

- AI 推荐
- 用户观察池
- 板块龙头
- 连续跟踪股票
- 用户手动添加

字段：

| 字段 | 说明 |
| --- | --- |
| 股票 | 名称 + 代码 |
| 综合评分 | 0-100 |
| 状态 | 待研究 / 跟踪中 / 已完成 |
| 更新时间 | 最近分析时间 |
| 下一步建议 | AI 自动生成 |

排序规则：

1. 风险最高
2. 买点出现
3. 热门板块
4. 用户关注度

## 9. Prototype Scope

本次原型已实现：

- Workspace 顶部栏
- Sidebar
- Market Pulse
- AI Daily Brief
- Research Queue
- Hot Sectors 预览
- Watchlist Changes 摘要
- Risk Alerts
- AI Copilot 可折叠面板
- 键盘快捷键 1-8

Part 2 将继续实现：

- Hot Sectors 完整页
- Watchlist 完整交互
- AI Copilot 对话
- Loading / Empty / Error
- API 设计
