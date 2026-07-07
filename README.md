# AlphaLens AI

AlphaLens AI 是一个面向 A 股研究的 AI 股票研究助手。它不是荐股或自动交易软件，而是帮助用户从市场、板块、个股、资金、基本面、消息面和风险维度建立研究流程的产品原型。

## v0.1 Foundation

本阶段目标是把仓库从普通代码仓库升级为可持续开发的产品仓库，为后续 PRD、UI、开发和 AI Agent 协作提供统一基础。

当前 MVP 范围：

- 市场首页
- 热门板块
- 股票详情
- AI 研究报告
- 综合评分
- 观察池
- AI 聊天

暂不开发：

- 自动交易
- 回测
- 多账户
- 社区

## 目录结构

```text
AlphaLens/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── docs/
├── design/
├── frontend/
├── backend/
├── database/
├── api/
├── agents/
├── prompts/
├── scripts/
├── assets/
└── prototype/
```

## 技术架构

- 前端目标栈：React、Next.js、Tailwind CSS
- 后端当前栈：FastAPI
- 后端目标栈：FastAPI、PostgreSQL、Redis
- AI 目标能力：多 Agent、RAG、LLM

## 当前可运行原型

当前 FastAPI 后端仍服务 `prototype/static` 下的静态原型。

安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010
```

打开：

```text
http://127.0.0.1:8010
```

测试：

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests
```

如果本机安装了其他 pytest 插件导致冲突，可使用项目脚本：

```powershell
.\scripts\test.ps1
```

## 数据口径

当前数据来自公开行情接口、本地样例研究库和原型阶段聚合逻辑，仅用于研究流程验证，不构成投资建议。高分不代表一定上涨，低分不代表一定下跌；风险提示优先于买点提示。
