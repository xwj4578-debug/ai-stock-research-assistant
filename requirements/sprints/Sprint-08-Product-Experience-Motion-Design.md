# Sprint 08 --- Product Experience & Motion Design

**Project:** AlphaLens AI\
**Stage:** Product Experience Upgrade\
**Goal:** 把 AlphaLens 从"后台系统"升级为"专业 AI 投资研究产品"。

------------------------------------------------------------------------

# 1. Sprint Objective

本 Sprint 不新增业务功能。

重点提升：

-   产品高级感
-   品牌一致性
-   页面动效
-   微交互
-   信息层级
-   AI 产品体验

完成后目标：

> 第一眼就让用户觉得这是一个专业、现代、可信赖的 AI 投资研究平台。

------------------------------------------------------------------------

# 2. Design Benchmark

参考产品：

-   Apple
-   Linear
-   Raycast
-   Arc Browser
-   Perplexity
-   Bloomberg Terminal（信息密度）
-   Notion（留白与阅读体验）

注意：

**参考体验，不复制视觉。**

------------------------------------------------------------------------

# 3. Design Principles

1.  Less but Better（少即是多）
2.  Motion with Purpose（动画服务于理解）
3.  Research First（研究优先）
4.  Explainable AI（AI 可解释）
5.  Calm UI（不过度炫技）
6.  Consistent Design（统一设计语言）

------------------------------------------------------------------------

# 4. Visual Upgrade

## Color

统一 Design Tokens：

-   Primary
-   Surface
-   Background
-   Border
-   Success
-   Warning
-   Danger
-   AI Accent

不要在组件内直接写颜色。

------------------------------------------------------------------------

## Typography

统一：

-   页面标题
-   模块标题
-   卡片标题
-   正文
-   数字
-   Caption

数字信息（评分、涨跌幅）层级明显。

------------------------------------------------------------------------

## Spacing

统一间距：

-   8
-   12
-   16
-   20
-   24
-   32

不要出现随机 padding。

------------------------------------------------------------------------

# 5. Motion Design

引入：

-   Framer Motion

统一动画：

## Page

-   Fade In
-   200\~300ms

## Card

-   Stagger Entrance
-   Hover Lift (2\~4px)

## Button

-   Hover
-   Press
-   Focus

## Number

-   Count Up Animation

## AI Message

-   Typewriter Effect
-   Streaming Ready

------------------------------------------------------------------------

# 6. Workspace Improvements

## Market Pulse

增加：

-   分数数字动画
-   趋势箭头动画
-   Hover 查看详细指标

------------------------------------------------------------------------

## AI Daily Brief

增加：

-   展开动画
-   长报告弹窗
-   阅读时间提示

------------------------------------------------------------------------

## Research Queue

优化：

-   卡片高度统一
-   状态 Badge
-   一键开始研究
-   完成状态动画

------------------------------------------------------------------------

## Hot Sectors

增加：

-   Hover 高亮
-   点击过渡
-   热度 Badge

------------------------------------------------------------------------

## AI Research Assistant

改为真正聊天布局：

Header

↓

Quick Actions

↓

Conversation

↓

Input

↓

Status

支持：

-   Enter 发送
-   Shift+Enter 换行
-   Loading
-   Streaming

------------------------------------------------------------------------

# 7. Empty / Loading / Error

统一设计：

Loading：

-   Skeleton

Empty：

-   Illustration
-   下一步按钮

Error：

-   Retry
-   错误说明

------------------------------------------------------------------------

# 8. Toast & Feedback

统一：

-   成功
-   警告
-   错误
-   信息

动画：

-   Slide Up
-   Auto Close

------------------------------------------------------------------------

# 9. Icons

统一使用：

Lucide React

禁止混用多个图标库。

------------------------------------------------------------------------

# 10. Responsive

支持：

-   1920
-   1440
-   1280

1280 以下：

AI 面板允许折叠。

------------------------------------------------------------------------

# 11. Performance

目标：

-   首屏 \< 2 秒
-   动画 60 FPS
-   Skeleton 替代白屏
-   避免布局抖动（CLS）

------------------------------------------------------------------------

# 12. Deliverables

Codex 完成：

-   接入 Framer Motion
-   建立统一 Design Tokens
-   优化 Typography
-   完善 Hover / Focus / Active
-   AI 聊天布局升级
-   Skeleton Loading
-   Toast 系统
-   统一 Badge
-   优化卡片布局
-   添加页面转场

------------------------------------------------------------------------

# 13. Acceptance Criteria

必须满足：

-   页面默认中文
-   动画自然，不影响性能
-   视觉风格统一
-   信息层级清晰
-   无明显布局跳动
-   深色主题一致
-   无控制台报错

------------------------------------------------------------------------

# 14. Codex Prompt

请在当前 AlphaLens 项目基础上完成 Product Experience & Motion Design。

要求：

1.  不新增业务功能。
2.  使用 Framer Motion 增强页面体验。
3.  建立统一 Design Tokens。
4.  全站统一字体、间距、颜色。
5.  AI 助手升级为聊天体验。
6.  完善 Loading / Empty / Error。
7.  增加 Hover、Focus、Transition。
8.  保持金融专业风格。
9.  不影响现有数据接口。
10. 保持代码可维护、组件化。

------------------------------------------------------------------------

# Next Sprint

Sprint 09 ------ AI Engine (LLM Integration)

完成：

-   AI Daily Report
-   AI Research Report
-   AI Explain Score
-   AI Copilot 接入 LLM
-   Prompt 管理
