# Component Spec

Version: v0.2 Sprint 1

## 1. Button

### Variants

- Primary：主操作，例如“生成报告”“加入观察池”
- Secondary：次级操作，例如“查看详情”
- Ghost：弱操作，例如“取消”
- Danger：风险操作，例如“移出观察池”

### States

- Default
- Hover
- Active
- Disabled
- Loading

### Rules

- 主要按钮最多每个区域一个。
- 危险操作必须使用 Danger 样式，且文案清晰。
- 按钮高度默认 40px，紧凑按钮 32px。

## 2. Input

用于普通文本、数字、价格、备注输入。

规则：

- 默认高度 40px。
- 必须有 Label 或明确 placeholder。
- 错误状态需要显示具体原因。

## 3. Search Box

用于股票名称、代码、拼音首字母搜索。

结构：

- 搜索图标
- 输入框
- 清除按钮
- 搜索建议列表

状态：

- Empty
- Typing
- Loading
- Result
- No Result
- Error

## 4. Card

基础信息容器。

规则：

- 不允许卡片套卡片。
- 卡片内标题不使用页面级字号。
- 卡片必须有明确主题。

## 5. AI Summary Card

用于展示 AI 总结。

字段：

- 结论标题
- 关注等级
- 上涨/下跌逻辑
- 风险点
- 操作参考

规则：

- 不能输出绝对买卖指令。
- 风险提示必须高于买点提示。

## 6. Score Card

用于综合评分和分项评分。

字段：

- 分数
- 等级
- 分项解释
- 数据来源

规则：

- 综合分不能单独做成买入信号。
- 风险分必须说明“越高越危险”。

## 7. Risk Card

用于风险提示。

字段：

- 风险等级
- 风险原因
- 触发条件
- 后续观察点

规则：

- 高风险使用强视觉提示。
- 风险卡优先级高于买点卡。

## 8. Sector Card

用于热门板块。

字段：

- 板块名称
- 涨跌幅
- 成交额
- 主力净流入
- 涨停家数
- 龙头股
- 热度评分
- 消息催化

## 9. Stock Card

用于股票列表和候选股。

字段：

- 股票名称
- 股票代码
- 所属板块
- 当前价格
- 涨跌幅
- 综合评分
- 技术状态
- 风险状态
- 操作入口

## 10. Watchlist Card

用于观察池。

字段：

- 股票名称
- 加入原因
- 当前评分
- 技术状态
- 资金状态
- 消息状态
- 风险等级
- 计划买点
- 止损参考

## 11. Dialog

用于确认、编辑和复杂选择。

规则：

- Desktop 居中 Modal。
- iPad 可用居中 Modal 或 Drawer。
- Mobile 后续使用 Bottom Sheet。

## 12. Drawer

用于 AI Assistant、筛选器、详情补充信息。

规则：

- Desktop 右侧滑出。
- 可折叠。
- 不阻断主内容浏览，除非为关键确认操作。

## 13. Toast

用于轻量反馈。

类型：

- Success
- Warning
- Error
- Info

默认 3 秒自动消失。

## 14. Loading

用于数据加载。

优先级：

- 页面级 Skeleton
- 区块级 Spinner
- 按钮内 Loading

## 15. Empty State

用于无数据场景。

必须包含：

- 原因
- 下一步动作

示例：观察池为空时提示“先从市场雷达加入股票”。

## 16. Error State

用于接口失败、数据源不可用。

必须包含：

- 错误原因
- 重试入口
- 是否影响核心判断

## 17. Skeleton

用于列表、卡片、图表加载中。

规则：

- 保持最终布局尺寸，避免加载后跳动。
- 图表区域必须保留固定高度。
