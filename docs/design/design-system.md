# AlphaLens AI Design System

Version: v0.2 Sprint 1

## 1. 设计目标

在正式开发页面之前，先建立统一的视觉、交互和组件规范。AlphaLens AI 是金融研究工具，界面应当克制、清晰、可扫描，重点帮助用户理解市场、板块、个股、风险和观察池状态。

## 2. Design Token

### Color

| Token | Value | 用途 |
| --- | --- | --- |
| `--color-primary` | `#2563eb` | 主按钮、链接、选中状态 |
| `--color-primary-hover` | `#1d4ed8` | 主按钮 hover |
| `--color-success` | `#11845b` | 防守、支撑、低风险、成功状态 |
| `--color-risk` | `#d93025` | 上涨、风险、高热度、危险提示 |
| `--color-warning` | `#b7791f` | 分歧、观察、中性警告 |
| `--color-text` | `#14202b` | 主文本 |
| `--color-muted` | `#637083` | 次级文本 |
| `--color-line` | `#dce4ee` | 分割线、边框 |
| `--color-bg` | `#f3f6fa` | 页面背景 |
| `--color-surface` | `#ffffff` | 卡片、面板 |
| `--color-soft-blue` | `#eef4ff` | 主色浅背景 |
| `--color-soft-red` | `#fff1f0` | 风险浅背景 |
| `--color-soft-green` | `#edf8f3` | 支撑/低风险浅背景 |
| `--color-soft-yellow` | `#fff8e6` | 观察浅背景 |

### Semantic Rule

- 红色可用于 A 股语境中的上涨和强热度，也可用于风险提示。风险场景必须配文字，不只靠颜色。
- 绿色用于下跌、防守、支撑、低风险和成功状态。
- 黄色用于观察、分歧和不确定。
- 蓝色只用于系统操作，不用于涨跌判断。

## 3. Typography

| Token | Size | Line Height | Weight | 用途 |
| --- | --- | --- | --- | --- |
| H1 | 32px | 40px | 800 | 页面标题 |
| H2 | 26px | 34px | 800 | 模块主标题 |
| H3 | 20px | 28px | 800 | 卡片组标题 |
| H4 | 16px | 24px | 800 | 卡片标题 |
| Body | 15px | 24px | 400 | 正文 |
| Caption | 13px | 20px | 400 | 说明、来源、更新时间 |
| Label | 14px | 20px | 700 | 表单标签、字段名 |
| Number | 28px | 34px | 900 | 价格、评分、关键数值 |

字体栈：

```css
font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
```

## 4. Spacing

统一使用 4px 基准：

| Token | Value | 用途 |
| --- | --- | --- |
| `space-1` | 4px | 小图标间距 |
| `space-2` | 8px | 标签、按钮内部间距 |
| `space-3` | 12px | 卡片内部紧凑间距 |
| `space-4` | 16px | 卡片 padding、模块间距 |
| `space-6` | 24px | 页面区块间距 |
| `space-8` | 32px | 大区块间距 |
| `space-12` | 48px | 页面主视觉间距 |

## 5. Radius

| Token | Value | 用途 |
| --- | --- | --- |
| `radius-card` | 12px | 普通卡片 |
| `radius-button` | 10px | 按钮 |
| `radius-dialog` | 16px | Dialog / Modal |
| `radius-input` | 10px | 输入框 |
| `radius-pill` | 999px | Tag / Badge |

## 6. Shadow

| Token | Value | 用途 |
| --- | --- | --- |
| `shadow-card` | `0 8px 24px rgba(20, 32, 43, 0.06)` | 普通卡片 |
| `shadow-floating` | `0 12px 32px rgba(20, 32, 43, 0.12)` | 悬浮工具栏、抽屉 |
| `shadow-modal` | `0 24px 80px rgba(20, 32, 43, 0.22)` | Modal |

## 7. Icons

推荐使用 Lucide Icons。

规则：

- 操作按钮优先使用 icon + tooltip。
- 主要动作可使用 icon + text。
- 不手绘 SVG 图标，除非 Lucide 没有对应图标。
- 图标大小默认 18px；紧凑按钮使用 16px。

## 8. Charts

| 类型 | 图表库 | 用途 |
| --- | --- | --- |
| 金融图表 | ECharts | 指数、成交额、资金流 |
| K线图 | TradingView Widget | 股票详情 K 线 |
| 业务统计 | Recharts | 观察池、评分、分布统计 |

## 9. Desktop Layout

桌面端结构：

- 左侧导航：一级功能入口
- 顶部导航：搜索、账户、全局动作
- 主内容区：市场、板块、个股、观察池
- AI Assistant 面板：右侧可折叠

内容宽度建议：

- 1920：左导航 240px，AI 面板 360px，主内容自适应
- 1440：左导航 220px，AI 面板 320px
- 1280：左导航 200px，AI 面板默认折叠
- iPad：顶部导航 + 折叠菜单
- Mobile：第二阶段单独定义

## 10. Responsive

本阶段支持设计约束：

- 1920
- 1440
- 1280
- iPad

Mobile 在第二阶段补完整规范。
