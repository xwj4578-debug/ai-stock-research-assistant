# Sprint 06 --- Research Engine Foundation (Revised)

**Project:** AlphaLens AI\
**Stage:** Core Capability - Research Engine\
**Revision:** Configuration-Driven Rules

------------------------------------------------------------------------

# 1. Goal

完成 AlphaLens 第一版 **Research Engine**。

Research Engine 是 AlphaLens 的核心能力，不负责获取数据，也不负责生成 AI
文本。

负责：

-   综合评分（Scoring）
-   排序（Ranking）
-   风险评估（Risk）
-   研究建议（Recommendation）

------------------------------------------------------------------------

# 2. Core Design Principles（新增）

Research Engine 必须遵循以下原则：

1.  **Configuration First**
    -   所有评分规则、权重、阈值必须配置化。
    -   禁止在 Python 代码中写死评分公式（No Magic Numbers）。
2.  **Explainable**
    -   每个分数都必须能解释来源。
    -   返回总分的同时返回各维度得分。
3.  **Testable**
    -   每个 Engine 可独立单元测试。
    -   不依赖 Provider、数据库或 LLM。
4.  **Market Agnostic**
    -   评分模板可扩展到 A 股、港股、美股、ETF。

------------------------------------------------------------------------

# 3. Architecture

``` text
Workspace
    │
Application Service
    │
Research Engine
├── Scoring Engine
├── Ranking Engine
├── Risk Engine
└── Recommendation Engine
    │
Repository
    │
Provider
```

------------------------------------------------------------------------

# 4. Configuration Driven Design（新增）

新增目录：

``` text
backend/app/domain/config/
├── scoring.yaml
├── ranking.yaml
├── risk.yaml
├── recommendation.yaml
└── market-profile.yaml
```

说明：

### scoring.yaml

维护所有评分权重，例如：

``` yaml
market: 20
sector: 20
trend: 20
volume: 15
capital: 15
risk: 10
```

### ranking.yaml

维护排序规则：

-   热点优先
-   风险降权
-   用户观察池加权

### risk.yaml

维护：

-   风险等级
-   波动阈值
-   连板风险
-   放量下跌风险

### recommendation.yaml

维护：

-   推荐文案模板
-   下一步建议规则
-   研究优先级

### market-profile.yaml

支持未来不同市场：

``` yaml
cn_a:
hk:
us:
etf:
```

不同市场可采用不同评分策略。

------------------------------------------------------------------------

# 5. Explainable Score（新增）

ResearchResult 增加评分拆解：

``` json
{
  "totalScore": 91,
  "details": {
    "market": 18,
    "sector": 19,
    "trend": 17,
    "volume": 14,
    "capital": 15,
    "risk": 8
  }
}
```

前端可以直接展示：

> 为什么是 91 分？

而不是一个黑盒数字。

------------------------------------------------------------------------

# 6. Development Rules（新增）

Codex 必须遵守：

-   禁止硬编码评分。
-   所有权重读取 YAML。
-   所有阈值读取 YAML。
-   所有 Recommendation 模板读取 YAML。
-   所有 Engine 必须支持单元测试。
-   Domain 不允许 import Provider。
-   Domain 不允许 import AKShare。

------------------------------------------------------------------------

# 7. Acceptance Criteria（更新）

除原有要求外，还必须满足：

-   所有评分规则配置化。
-   修改 YAML 后无需修改 Python 代码即可调整评分。
-   返回评分详情。
-   支持未来新增市场模板。
-   单元测试覆盖各 Engine。

------------------------------------------------------------------------

# 8. Updated Codex Tasks

新增任务：

1.  创建 `backend/app/domain/config/`。
2.  编写 `scoring.yaml`。
3.  编写 `ranking.yaml`。
4.  编写 `risk.yaml`。
5.  编写 `recommendation.yaml`。
6.  编写 `market-profile.yaml`。
7.  所有 Engine 从 YAML 读取配置。
8.  API 返回评分拆解（score details）。
9.  为 YAML 配置增加示例与默认值。
10. 编写配置加载测试。

------------------------------------------------------------------------

# Why This Revision

Research Engine 是 AlphaLens 的核心资产。

通过配置驱动：

-   可以快速调整策略；
-   可以支持不同市场；
-   可以支持不同投资风格；
-   可以避免评分逻辑散落在代码中；
-   为未来 AI Explain、策略回测、多策略引擎打下基础。
