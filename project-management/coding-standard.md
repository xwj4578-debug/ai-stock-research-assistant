# Coding Standard

## General

- 保持模块边界清晰。
- 不为短期速度牺牲长期架构。
- 避免无解释的复杂抽象。
- 所有外部数据源都要有失败兜底。

## Backend

- FastAPI 路由保持薄层。
- 业务逻辑放在服务模块。
- 数据源调用需要超时、错误处理和缓存策略。
- 不在 API 中返回无法解释的评分。

## Frontend

- 使用 Design System 中定义的 token 和组件规范。
- 不使用横向大表格作为移动端主要展示。
- Loading / Empty / Error 必须有明确状态。
