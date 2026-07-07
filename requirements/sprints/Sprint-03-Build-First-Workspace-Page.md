# Sprint 03 --- Build First Accessible Workspace Page

**Goal:**\
先做出一个可以在浏览器访问的 AlphaLens Workspace
页面，不接真实数据，使用 mock 数据完成产品雏形。

------------------------------------------------------------------------

## 1. Sprint Objective

本阶段目标不是完成完整产品，而是完成一个可访问页面：

``` text
http://localhost:3000
```

打开后可以看到：

-   左侧导航 Sidebar
-   顶部 Header
-   Market Pulse 市场脉搏卡片
-   AI Daily Brief
-   Research Queue
-   Hot Sectors
-   Watchlist
-   Risk Alerts
-   右侧 AI Copilot 面板

------------------------------------------------------------------------

## 2. Recommended Tech Stack

Frontend:

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   shadcn/ui
-   lucide-react

暂时不接后端。

数据全部使用 mock。

------------------------------------------------------------------------

## 3. Target Directory Structure

``` text
frontend/
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │   └── Topbar.tsx
│   ├── workspace/
│   │   ├── MarketPulseCard.tsx
│   │   ├── DailyBriefCard.tsx
│   │   ├── ResearchQueue.tsx
│   │   ├── HotSectors.tsx
│   │   ├── Watchlist.tsx
│   │   ├── RiskAlerts.tsx
│   │   └── AiCopilot.tsx
│   └── ui/
├── lib/
│   └── mock-data.ts
└── types/
    └── workspace.ts
```

------------------------------------------------------------------------

## 4. Page Layout

``` text
┌───────────────────────────────────────────────────────────────┐
│ Topbar: AlphaLens | Search | Notification | Profile           │
├───────────────┬─────────────────────────────────────┬─────────┤
│ Sidebar       │ Main Workspace                      │ AI      │
│               │                                     │ Copilot │
│ Workspace     │ Market Pulse                        │         │
│ Market        │ AI Daily Brief                      │         │
│ Sector        │ Research Queue                      │         │
│ Stocks        │ Hot Sectors                         │         │
│ Watchlist     │ Watchlist                           │         │
│ Review        │ Risk Alerts                         │         │
└───────────────┴─────────────────────────────────────┴─────────┘
```

Desktop-first.

------------------------------------------------------------------------

## 5. Visual Style

整体风格：

-   深色背景
-   卡片式布局
-   专业金融终端感
-   不要太花哨
-   信息清晰优先

建议颜色：

``` text
background: #0B1020
panel: #111827
card: #172033
border: #263244
primary: #4F8BFF
success: #22C55E
danger: #EF4444
warning: #F59E0B
text-primary: #F9FAFB
text-secondary: #9CA3AF
```

------------------------------------------------------------------------

## 6. Mock Data

在 `lib/mock-data.ts` 中创建 mock 数据。

### marketPulse

``` ts
export const marketPulse = {
  score: 78,
  status: "偏强",
  turnover: "1.28 万亿",
  upCount: 3621,
  downCount: 1587,
  limitUp: 86,
  limitDown: 9,
  brokenRate: "18%",
  leadingHeight: "5 连板",
  summary: "今日市场情绪偏强，机器人、AI算力和半导体方向表现活跃。"
};
```

### dailyBrief

``` ts
export const dailyBrief = {
  title: "AI Daily Brief",
  content:
    "今日市场情绪回暖，资金主要集中在机器人、AI算力和半导体方向。短线情绪有所修复，但高位股分歧仍然明显，建议优先研究热点板块中的趋势中军。",
};
```

### researchQueue

``` ts
export const researchQueue = [
  {
    code: "601138",
    name: "工业富联",
    score: 91,
    status: "待研究",
    reason: "AI服务器与算力产业链核心标的，资金持续关注。",
  },
  {
    code: "300308",
    name: "中际旭创",
    score: 88,
    status: "跟踪中",
    reason: "CPO方向趋势中军，机构关注度较高。",
  },
  {
    code: "002156",
    name: "通富微电",
    score: 84,
    status: "待研究",
    reason: "半导体封测方向活跃，板块热度提升。",
  },
];
```

### hotSectors

``` ts
export const hotSectors = [
  {
    name: "机器人",
    change: "+4.82%",
    score: 92,
    leader: "巨轮智能",
    reason: "政策催化叠加产业消息发酵，板块涨停家数较多。",
  },
  {
    name: "AI算力",
    change: "+3.76%",
    score: 89,
    leader: "工业富联",
    reason: "AI服务器需求持续提升，资金关注度高。",
  },
  {
    name: "半导体",
    change: "+2.91%",
    score: 85,
    leader: "通富微电",
    reason: "国产替代与封测方向走强。",
  },
];
```

### watchlist

``` ts
export const watchlist = [
  {
    code: "601138",
    name: "工业富联",
    score: 91,
    risk: "Medium",
    nextAction: "等待回踩5日线",
  },
  {
    code: "002415",
    name: "海康威视",
    score: 76,
    risk: "Low",
    nextAction: "继续观察",
  },
];
```

------------------------------------------------------------------------

## 7. Component Requirements

### AppShell

负责整体布局：

-   Sidebar 固定宽度 240px
-   Topbar 高度 64px
-   Main 内容自适应
-   AI Copilot 右侧固定宽度 360px

------------------------------------------------------------------------

### Sidebar

导航项：

-   Workspace
-   Market
-   Sector
-   Stocks
-   Watchlist
-   Research Reports
-   Review
-   Settings

当前选中 Workspace。

------------------------------------------------------------------------

### Topbar

包含：

-   Logo：AlphaLens
-   搜索框 placeholder：搜索股票 / 板块 / 问 AI
-   通知按钮
-   用户头像占位

------------------------------------------------------------------------

### MarketPulseCard

展示：

-   市场情绪评分
-   市场状态
-   成交额
-   上涨/下跌家数
-   涨停/跌停
-   炸板率
-   连板高度
-   AI总结

------------------------------------------------------------------------

### DailyBriefCard

展示 AI 今日摘要。

按钮：

-   展开全文
-   生成长报告

按钮暂时只做 UI，不实现逻辑。

------------------------------------------------------------------------

### ResearchQueue

展示待研究股票列表。

每个 item 包含：

-   股票名称
-   股票代码
-   综合评分
-   状态
-   AI 研究理由

按钮：

-   开始研究
-   加入观察池

暂时只做 UI。

------------------------------------------------------------------------

### HotSectors

展示热点板块。

每个 item 包含：

-   板块名称
-   涨跌幅
-   热度评分
-   龙头股
-   AI 解释

------------------------------------------------------------------------

### Watchlist

展示观察池股票。

包含：

-   股票名称
-   评分
-   风险等级
-   下一步动作

------------------------------------------------------------------------

### RiskAlerts

展示风险提醒。

Mock 示例：

``` ts
[
  "高位连板股分歧加大，注意炸板风险。",
  "AI算力方向短线涨幅较大，避免盲目追高。",
  "市场成交额虽放大，但部分板块轮动较快。"
]
```

------------------------------------------------------------------------

### AiCopilot

右侧 AI 面板。

包含：

-   标题：AI Research Copilot
-   简短说明
-   快捷问题按钮：
    -   今天应该研究什么？
    -   为什么机器人板块上涨？
    -   帮我对比工业富联和中际旭创
    -   今天有哪些风险？
-   输入框
-   Send 按钮

暂时不接真实 AI。

------------------------------------------------------------------------

## 8. Acceptance Criteria

完成后必须满足：

-   `npm run dev` 可以启动
-   浏览器访问 `http://localhost:3000`
-   页面没有报错
-   所有模块展示 mock 数据
-   页面整体是深色专业风格
-   组件拆分清晰
-   后续可以继续接 API
-   不出现真实荐股语句
-   页面底部或 README 需保留风险提示：仅用于研究，不构成投资建议

------------------------------------------------------------------------

## 9. Codex Prompt

请 Codex 按以下要求实现：

``` text
请在当前仓库中实现 AlphaLens 第一版可访问 Workspace 页面。

要求：
1. 使用 Next.js + React + TypeScript + Tailwind CSS。
2. 在 frontend/ 目录下创建前端项目。
3. 实现 AppShell、Sidebar、Topbar、MarketPulseCard、DailyBriefCard、ResearchQueue、HotSectors、Watchlist、RiskAlerts、AiCopilot 组件。
4. 所有数据先使用 lib/mock-data.ts。
5. 页面访问地址为 http://localhost:3000。
6. 风格为深色专业金融研究工作台。
7. 不接后端，不接真实股票数据，不接真实 AI。
8. 保持代码结构清晰，方便后续接 API。
9. 页面必须包含风险提示：本产品仅用于投资研究，不构成投资建议。
10. 完成后确保 npm run dev 正常启动。
```

------------------------------------------------------------------------

## 10. Next Step

完成本 Sprint 后，下一步进入：

**Sprint 04 --- Connect Workspace Mock API**

目标：

-   建立 FastAPI 后端
-   提供 `/api/v1/workspace`
-   前端从 mock file 改为请求本地 API
-   保留 mock fallback
