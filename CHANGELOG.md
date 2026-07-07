# Changelog

## v1.4.0 - Sprint 04 Interactive Workspace Mock

- Added interactive mock behavior for daily brief, research queue, sector detail, watchlist, report modal, and AI Copilot.
- Added Normal / Loading / Empty / Error workspace state toggle.
- Added `locales/zh-CN.json` and `t()` i18n foundation with Chinese product copy.
- Localized navigation, module names, search placeholder, buttons, toast, and risk notice.

## v1.3.0 - Sprint 03 First Workspace Page

- Reorganized `requirements/` into `foundation/`, `sprints/`, and `chapters/`.
- Added a Next.js + React + TypeScript + Tailwind frontend under `frontend/`.
- Implemented the first accessible mock Workspace page on port `3000`.
- Added mock Market Pulse, AI Daily Brief, Research Queue, Hot Sectors, Watchlist, Risk Alerts, and AI Copilot modules.

## v1.2.0 - Research Workspace Parts 2-4

- Added Hot Sectors interaction, sector detail, Watchlist cards, and AI Copilot structured actions.
- Added workspace loading, empty, error, module refresh, queue completion, and queue removal states.
- Added `/api/v1/workspace`, `/api/v1/watchlist`, queue action, and telemetry draft APIs.
- Added Research Workspace Part 2, Part 3, and Part 4 documentation.

## v0.1.0 - Foundation

- 建立 AlphaLens AI 产品仓库目录。
- 迁移后端代码到 `backend/app`。
- 迁移静态原型到 `prototype/static`。
- 增加 `docs`、`design`、`frontend`、`database`、`api`、`agents`、`prompts`、`scripts`、`assets` 等基础目录。
- 增加项目 README、Roadmap、Contribution、License 和基础文档索引。

## v0.2.0 - Sprint 1 Design System

- 建立 `requirements/` 目录，用于归档每次需求迭代。
- 新增 `docs/design/design-system.md`。
- 新增 `docs/design/component-spec.md`。
- 建立 `frontend/src/components`、`frontend/src/styles`、`frontend/src/lib`、`frontend/src/types` 目录。
- 明确 Design Token、Typography、Spacing、Radius、Shadow、Icons、Charts、Desktop Layout 和响应式约束。

## v1.0.0 - Chapter 05 Research Workspace Part 1

- 新增 Research Workspace 产品设计文档。
- 原型首页升级为 Workspace 布局。
- 增加顶部栏、左侧导航、Market Pulse、AI Daily Brief、Research Queue、Risk Alerts 和 AI Copilot。
- 支持 Sidebar 键盘快捷键 1-8。

## v1.1.0 - Project Foundation Guide

- 增加 `project-management/` 长期工程规范目录。
- 增加 `governance/` 项目治理目录。
- 增加 `examples/` 和根级 `tests/` 目录入口。
- 增加 ADR 机制和前三个 ADR。
- 增加 Research Workspace 章节化 docs 目录。
- 归档 `AlphaLens_Project_Foundation_Guide_v1.1.txt`。
