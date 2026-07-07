# Sprint 04 --- Interactive Workspace Mock

**Goal:**\
在现有 Workspace 页面基础上，把静态 mock 页面升级为可交互原型。\
本阶段仍然不接真实后端、不接真实股票数据、不接真实 AI。

------------------------------------------------------------------------

## 1. Current Review

当前页面已经完成：

-   Sidebar
-   Topbar
-   Workspace 主页面
-   Market Pulse
-   AI Daily Brief
-   Research Queue
-   AI Research Copilot
-   深色专业风格
-   Mock 数据提示

整体方向正确，可以进入交互增强阶段。

------------------------------------------------------------------------

## 2. Sprint Objective

本 Sprint 的目标：

让页面从"能看"变成"能点、能操作、能反馈"。

完成后用户可以：

-   展开 / 收起 AI Daily Brief
-   点击"生成长报告"展示 mock 报告
-   点击"开始研究"打开股票研究抽屉
-   点击"加入观察池"
-   在 Watchlist 中删除 / Pin 股票
-   点击热点板块查看板块详情 mock 弹窗
-   使用 AI Copilot 快捷问题
-   输入问题后得到 mock AI 回复
-   各模块支持 loading / empty / error mock 状态

------------------------------------------------------------------------

## 3. Do Not Do Yet

本阶段不要做：

-   真实后端
-   真实 AI API
-   真实股票行情
-   登录系统
-   数据库
-   自动交易
-   复杂图表

------------------------------------------------------------------------

## 4. New Components

建议新增组件：

``` text
frontend/components/workspace/
├── StockResearchDrawer.tsx
├── SectorDetailModal.tsx
├── MockReportModal.tsx
├── WorkspaceStatusToggle.tsx
├── EmptyState.tsx
├── ErrorState.tsx
└── LoadingSkeleton.tsx
```

------------------------------------------------------------------------

## 5. Interaction Requirements

### 5.1 AI Daily Brief

按钮：

-   展开全文
-   收起
-   生成长报告

交互：

-   默认展示短摘要
-   点击"展开全文"展示完整 mock 内容
-   点击"生成长报告"打开 `MockReportModal`

------------------------------------------------------------------------

### 5.2 Research Queue

每个股票 item 增加操作：

-   开始研究
-   加入观察池
-   标记完成

交互：

#### 开始研究

点击后打开右侧或居中的 `StockResearchDrawer`。

Drawer 内容：

-   股票名称
-   股票代码
-   综合评分
-   所属板块
-   AI 核心结论
-   上涨逻辑
-   风险提示
-   下一步建议

#### 加入观察池

点击后：

-   如果股票不在 watchlist，加入 watchlist
-   显示 toast：已加入观察池
-   如果已存在，显示 toast：已在观察池中

#### 标记完成

点击后：

-   item 状态变成"已完成"
-   UI 降低透明度
-   可通过"恢复"按钮恢复

------------------------------------------------------------------------

### 5.3 Hot Sectors

每个板块卡片可点击。

点击后打开 `SectorDetailModal`。

Modal 内容：

-   板块名称
-   今日涨跌幅
-   热度评分
-   龙头股
-   趋势中军
-   补涨股
-   AI 板块总结
-   主要风险
-   相关股票列表

------------------------------------------------------------------------

### 5.4 Watchlist

每个观察池 item 支持：

-   Pin
-   删除
-   查看研究报告

交互：

-   Pin 后置顶
-   删除后从列表移除
-   如果 watchlist 为空，展示 EmptyState

------------------------------------------------------------------------

### 5.5 AI Copilot

支持两种 mock 交互：

#### 快捷问题

点击快捷问题后：

-   输入框自动填入问题
-   生成 mock answer

快捷问题：

-   今天应该研究什么？
-   为什么机器人板块上涨？
-   对比工业富联和中际旭创
-   今天有哪些风险？

#### 手动输入

用户输入问题并点击 Send：

-   显示 loading 600ms
-   输出 mock answer
-   追加到对话列表

------------------------------------------------------------------------

## 6. Mock AI Answers

在 `lib/mock-ai.ts` 中新增：

``` ts
export const mockAiAnswers = {
  "今天应该研究什么？":
    "建议先研究机器人、AI算力和半导体三个方向。优先查看板块内趋势中军，而不是直接追高连板股。",
  "为什么机器人板块上涨？":
    "机器人板块上涨主要来自政策催化、产业消息发酵和短线资金回流。需要注意高位股分歧与炸板风险。",
  "对比工业富联和中际旭创":
    "工业富联更偏 AI 服务器和算力基础设施，中际旭创更偏 CPO 光模块方向。前者偏容量中军，后者弹性更高。",
  "今天有哪些风险？":
    "主要风险包括高位股分歧、热点轮动过快、部分 AI 算力方向短线涨幅较大，以及市场量能是否持续。"
};
```

------------------------------------------------------------------------

## 7. State Mock

新增 `WorkspaceStatusToggle`，仅开发阶段使用。

支持切换：

-   Normal
-   Loading
-   Empty
-   Error

用途：

测试组件状态。

------------------------------------------------------------------------

## 8. UI Improvements

基于当前截图，建议优化：

### 8.1 右侧 AI Copilot

当前右侧面板略宽，可以保持 360px，但内容密度需要优化：

-   快捷问题按钮高度保持一致
-   Draft Answer 区域改成聊天流
-   输入框固定在底部
-   支持滚动

### 8.2 Research Queue

当前第一条 item 只露出上半部分，建议：

-   主内容区域允许滚动
-   卡片间距减小
-   Research Queue item 高度控制在 96px\~128px

### 8.3 顶部提示

`Mock data · No backend · No real AI` 保留，但建议放到页面右上角 badge。

### 8.4 风险提示

页面底部必须显示：

> 本产品仅用于投资研究与学习，不构成任何投资建议。

------------------------------------------------------------------------

## 9. Suggested State Management

本阶段可以用 React `useState`。

暂时不需要 Zustand。

需要管理：

-   selectedStock
-   selectedSector
-   isResearchDrawerOpen
-   isSectorModalOpen
-   watchlist
-   researchQueue
-   dailyBriefExpanded
-   aiMessages
-   workspaceStatus

------------------------------------------------------------------------

## 10. Acceptance Criteria

完成后必须满足：

-   页面仍可通过 `npm run dev` 正常访问
-   所有按钮点击有反馈
-   AI Copilot 可以 mock 对话
-   Research Queue 可以打开股票研究抽屉
-   Hot Sectors 可以打开板块详情弹窗
-   Watchlist 可以添加、Pin、删除
-   支持 Normal / Loading / Empty / Error 状态切换
-   页面无控制台报错
-   不接真实 AI / 不接真实行情 / 不接真实后端
-   保留投资风险提示

------------------------------------------------------------------------

## 11. Codex Prompt

请 Codex 执行以下任务：

``` text
在当前 AlphaLens frontend 页面基础上，实现 Sprint 04 Interactive Workspace Mock。

要求：
1. 不接真实后端、不接真实 AI、不接真实股票数据。
2. 新增 StockResearchDrawer、SectorDetailModal、MockReportModal、WorkspaceStatusToggle、EmptyState、ErrorState、LoadingSkeleton 组件。
3. 实现 AI Daily Brief 展开/收起和生成 mock 长报告。
4. Research Queue 支持开始研究、加入观察池、标记完成。
5. Hot Sectors 支持点击打开板块详情 mock 弹窗。
6. Watchlist 支持 Pin、删除、查看报告。
7. AI Copilot 支持快捷问题和手动输入 mock 回复。
8. 增加 Normal / Loading / Empty / Error 状态切换。
9. 优化右侧 Copilot 面板，使其像聊天窗口。
10. 页面底部或固定位置保留风险提示：本产品仅用于投资研究与学习，不构成任何投资建议。
11. 保持深色专业金融研究风格。
12. 完成后确保 npm run dev 无报错。
```

------------------------------------------------------------------------

## 12. Next Sprint

Sprint 05 --- Local Mock API

目标：

-   新建 FastAPI 后端
-   提供 `/api/v1/workspace`
-   前端从 mock file 改成请求本地接口
-   保留 fallback mock 数据
