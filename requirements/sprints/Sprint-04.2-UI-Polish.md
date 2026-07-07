# Sprint 04.2 --- UI Polish & Product Feel

**Project:** AlphaLens AI\
**Stage:** Workspace Prototype Polish\
**Goal:** 在已有可访问 Workspace 页面基础上，进行 UI
打磨，让页面从"能用"提升到"像一个专业产品"。

------------------------------------------------------------------------

## 1. Sprint Objective

本 Sprint 不新增复杂业务功能，不接真实后端，不接真实行情，不接真实 AI。

目标是优化：

-   中文产品感
-   卡片层级
-   信息密度
-   字体层级
-   深色主题质感
-   交互反馈
-   右侧 AI 助手体验
-   风险提示
-   响应式布局

完成后，页面应更接近：

> 专业金融研究工作台，而不是普通 Dashboard Demo。

------------------------------------------------------------------------

## 2. Current UI Review

当前页面优点：

-   页面已经可访问
-   三栏布局清晰
-   左侧导航、主内容、右侧 AI 助手结构正确
-   深色风格方向正确
-   Market Pulse 卡片已经有金融终端感
-   Mock 数据说明清楚

当前需要改进：

-   部分英文仍然存在
-   字体层级还不够精致
-   卡片间距略大，信息密度可以更高
-   右侧 AI Copilot 更像表单，不像聊天助手
-   Research Queue 区域露出不完整
-   缺少统一 Toast / Loading / Empty / Error 风格
-   缺少底部风险提示
-   Mock Badge 位置可以更轻量
-   页面整体还可以更"高级"和更"中国 A 股产品化"

------------------------------------------------------------------------

## 3. Language & Copy Polish

### 3.1 Default Language

默认语言：

``` text
zh-CN
```

第一版所有文案默认中文。

### 3.2 Navigation Copy

  Current            New
  ------------------ ------------
  Workspace          研究工作台
  Market             市场概览
  Sector             热点板块
  Stocks             股票研究
  Watchlist          观察池
  Research Reports   研究报告
  Review             交易复盘
  Settings           系统设置

### 3.3 Module Copy

  Current               New
  --------------------- --------------
  Market Pulse          市场脉搏
  AI Daily Brief        AI 市场日报
  Research Queue        今日研究任务
  Hot Sectors           热点板块
  Risk Alerts           风险提醒
  AI Research Copilot   AI 研究助手
  Draft Answer          AI 分析
  Send                  发送

### 3.4 Product Subtitle

顶部 Logo 下方副标题：

``` text
AI 投资研究工作台
```

### 3.5 Search Placeholder

建议：

``` text
搜索股票、板块、概念、ETF……
```

------------------------------------------------------------------------

## 4. Visual System Polish

### 4.1 Color Tokens

建议统一颜色变量，不要在组件中散落硬编码。

``` css
:root {
  --bg-main: #0B1020;
  --bg-panel: #111827;
  --bg-card: #172033;
  --bg-card-hover: #1D2940;

  --border-soft: #263244;
  --border-strong: #334155;

  --text-primary: #F9FAFB;
  --text-secondary: #CBD5E1;
  --text-muted: #94A3B8;

  --primary: #4F8BFF;
  --primary-hover: #6A9DFF;

  --success: #22C55E;
  --danger: #EF4444;
  --warning: #F59E0B;
  --ai: #8B5CF6;
}
```

### 4.2 Financial Color Rules

A 股产品默认：

-   上涨：红色
-   下跌：绿色

但如果当前代码已经使用国际习惯：

-   上涨绿色
-   下跌红色

需要统一为配置项：

``` ts
const MARKET_COLOR_MODE = "CN";
```

第一版建议使用 A 股习惯：

``` text
上涨 / 涨停 / 资金流入：红色
下跌 / 跌停 / 资金流出：绿色
风险 / 警告：橙色或红色
AI / 研究：蓝紫色
```

------------------------------------------------------------------------

## 5. Typography Polish

### 5.1 字体建议

中文优先：

``` css
font-family:
  Inter,
  "PingFang SC",
  "Microsoft YaHei",
  "Noto Sans SC",
  sans-serif;
```

### 5.2 字体层级

  类型              字号   字重 用途
  --------------- ------ ------ ----------------
  Page Title        28px    700 今日研究工作台
  Section Title     18px    700 市场脉搏
  Card Title        15px    600 成交额
  Body              14px    400 正文
  Caption           12px    400 辅助说明
  Number Large      48px    800 市场评分
  Number Medium     24px    700 评分 / 涨跌
  Badge             12px    600 状态标签

### 5.3 Letter Spacing

英文小标题如 `TODAY` 可以保留，但建议减少英文。

如果保留视觉标签：

``` text
TODAY → 今日
AI SUMMARY → AI 摘要
MUST REVIEW → 必看任务
```

------------------------------------------------------------------------

## 6. Layout Polish

### 6.1 Overall Layout

保持三栏布局：

``` text
Sidebar: 240px
Main: flex-1
AI Copilot: 360px
Topbar: 64px
```

建议：

-   主内容最大宽度不固定，随屏幕自适应
-   右侧 AI 助手固定宽度，支持未来收起
-   主内容区域独立滚动
-   AI Copilot 区域独立滚动

### 6.2 Card Spacing

建议：

``` text
Page padding: 24px
Section gap: 16px
Card gap: 12px
Card padding: 20px
Small card padding: 16px
```

### 6.3 Research Queue 优化

当前 Research Queue 第一项下半部分被截断。

要求：

-   主内容区域允许垂直滚动
-   Research Queue item 高度控制在 96px \~ 128px
-   股票名称、代码、状态、评分、按钮在一行内更紧凑
-   研究理由最多两行，超出省略

------------------------------------------------------------------------

## 7. Card Design Polish

### 7.1 Base Card

统一卡片样式：

``` text
background: var(--bg-card)
border: 1px solid var(--border-soft)
border-radius: 16px
padding: 20px
box-shadow: none 或轻微阴影
```

Hover：

``` text
border-color: var(--primary)
background: var(--bg-card-hover)
transition: 160ms ease
```

### 7.2 Market Pulse Card

市场评分卡需要更突出。

建议布局：

``` text
市场情绪
78 偏强

今日市场情绪偏强，资金集中在机器人、AI 算力和半导体方向。
```

优化：

-   评分数字最大
-   状态标签靠近数字
-   AI 总结放底部
-   指标卡片更紧凑

### 7.3 AI Daily Brief

增加可读性：

-   摘要最多 2 行
-   展开后显示完整内容
-   按钮右对齐
-   "生成长报告"使用主按钮
-   "展开全文"使用次按钮

### 7.4 Research Queue

每个任务卡：

``` text
股票名称 代码 状态
AI 研究理由
综合评分    开始研究
```

状态颜色：

  状态       颜色
  ---------- ------
  待研究     蓝色
  跟踪中     紫色
  已完成     灰色
  风险升高   红色
  出现买点   橙色

### 7.5 Hot Sectors

板块卡增加：

-   热度评分
-   龙头股
-   AI 解释
-   点击态

### 7.6 Risk Alerts

风险提醒要醒目，但不要吓人。

建议：

-   橙色边框
-   小图标
-   每条风险独立 item
-   风险文案简洁

------------------------------------------------------------------------

## 8. AI Copilot Polish

### 8.1 Layout

右侧 AI 助手应更像聊天窗口。

结构：

``` text
Header
  AI 研究助手
  不直接荐股，只辅助研究

Quick Questions

Chat Messages

Input Area
```

### 8.2 Chat Message Style

用户消息：

-   右侧
-   蓝色或深蓝背景

AI 消息：

-   左侧
-   深色卡片背景
-   支持换行和列表

### 8.3 Quick Questions

快捷问题按钮：

-   高度一致
-   hover 有反馈
-   点击后直接生成 mock 回复
-   按钮文案不超过 18 个字

建议：

``` text
今天应该研究什么？
机器人为什么上涨？
对比工业富联和中际旭创
今天有哪些风险？
```

### 8.4 Input Area

输入框固定在底部。

要求：

-   支持 Enter 发送
-   Shift + Enter 换行
-   Send 按钮中文化为"发送"
-   空输入禁止发送

------------------------------------------------------------------------

## 9. Interaction Polish

### 9.1 Hover

所有可点击元素必须有 hover。

包括：

-   菜单
-   卡片
-   按钮
-   股票 item
-   板块 item
-   快捷问题

### 9.2 Active

当前菜单高亮：

-   蓝色背景
-   左侧小色条或 icon 高亮

### 9.3 Transition

统一：

``` css
transition: all 160ms ease;
```

避免动画太花。

### 9.4 Toast

统一 toast 文案：

``` text
已加入观察池
已从观察池移除
已标记为完成
已生成模拟研究报告
```

------------------------------------------------------------------------

## 10. State Polish

### 10.1 Loading

使用 Skeleton。

不要整页白屏。

### 10.2 Empty

空状态要给下一步动作。

例如观察池为空：

``` text
暂无观察股票
完成一次研究后，可以将股票加入观察池持续跟踪。
按钮：前往今日研究任务
```

### 10.3 Error

错误状态：

``` text
数据加载失败
请稍后重试，或查看本地 mock 数据。
按钮：重试
```

### 10.4 Mock 状态提示

当前：

``` text
Mock data · No backend · No real AI
```

建议中文化：

``` text
演示数据 · 未接入后端 · 未接入真实 AI
```

放在页面右上角 Badge。

------------------------------------------------------------------------

## 11. Risk Disclaimer

页面底部固定展示：

``` text
本产品仅用于投资研究与学习，不构成任何投资建议。市场有风险，投资需谨慎。
```

要求：

-   字体 12px
-   颜色 muted
-   不抢主视觉
-   但必须存在

------------------------------------------------------------------------

## 12. Responsive Polish

### 12.1 1920px

三栏完整显示。

### 12.2 1440px

右侧 AI Copilot 保持 340px \~ 360px。

### 12.3 1280px

允许右侧 AI Copilot 收起为按钮。

### 12.4 Mobile

当前阶段不重点适配。

但不能完全崩溃。

------------------------------------------------------------------------

## 13. Accessibility

要求：

-   按钮有 aria-label
-   输入框有 placeholder
-   颜色对比度足够
-   键盘可操作
-   focus ring 清晰

------------------------------------------------------------------------

## 14. Codex Tasks

请 Codex 按以下要求执行 UI 打磨：

``` text
请在当前 AlphaLens Workspace 页面基础上进行 Sprint 04.2 UI Polish。

要求：
1. 全面中文化页面菜单、标题、按钮、提示和 AI 助手文案。
2. 保持 AlphaLens 作为英文品牌名，副标题改为“AI 投资研究工作台”。
3. 建立或整理统一的颜色变量，保持深色专业金融研究风格。
4. 按 A 股习惯处理涨跌颜色：上涨偏红、下跌偏绿；如果暂不方便，至少将颜色规则抽成配置。
5. 优化字体层级：页面标题、模块标题、卡片标题、数字、正文要有明显层级。
6. 优化卡片间距和信息密度，使页面更像专业研究工作台。
7. 优化 Research Queue，避免内容被截断，item 高度控制在 96px~128px。
8. 将 AI Copilot 改成聊天流体验，包含快捷问题、消息列表、底部输入框。
9. 支持 Enter 发送，Shift+Enter 换行，空输入禁止发送。
10. 所有可点击元素增加 hover / active / focus 状态。
11. 增加统一 Toast 文案。
12. 增加 Loading / Empty / Error 的统一视觉组件。
13. Mock Badge 中文化为“演示数据 · 未接入后端 · 未接入真实 AI”。
14. 页面底部展示风险提示：“本产品仅用于投资研究与学习，不构成任何投资建议。市场有风险，投资需谨慎。”
15. 保持当前布局和组件结构，不要重构成完全不同的页面。
16. 不接真实后端、不接真实行情、不接真实 AI。
17. 完成后确保 npm run dev 正常运行，无控制台报错。
```

------------------------------------------------------------------------

## 15. Acceptance Criteria

完成后必须满足：

-   页面全部默认中文
-   页面不再出现明显英文业务文案
-   页面视觉更精致
-   Research Queue 不被截断
-   AI 研究助手更像聊天产品
-   所有按钮有交互反馈
-   Loading / Empty / Error 状态统一
-   风险提示存在
-   页面无控制台错误
-   不引入真实荐股语句
-   仍可通过 `http://localhost:3000` 正常访问

------------------------------------------------------------------------

## 16. Next Sprint

Sprint 05 --- Local Mock API

目标：

-   新建 FastAPI 后端
-   提供 `/api/v1/workspace`
-   前端从本地 API 获取 mock 数据
-   保留前端 fallback mock
-   开始建立前后端数据契约
