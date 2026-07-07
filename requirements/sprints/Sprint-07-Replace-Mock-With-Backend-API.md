# Sprint 07 --- Replace Frontend Mock With Backend API

**Project:** AlphaLens AI\
**Stage:** Frontend ↔ Backend Integration\
**Goal:** 将 Workspace 页面从前端本地 Mock 数据切换为后端 API
数据，默认使用真实/后端数据，Mock 仅作为降级 fallback。

------------------------------------------------------------------------

# 1. Current Situation

当前页面大概率仍然存在：

``` ts
import { marketPulse, researchQueue, hotSectors, watchlist } from "@/lib/mock-data";
```

这意味着：

-   页面展示的是前端写死的 Mock 数据
-   后端 Data Engine / Research Engine 即使完成，也没有真正驱动前端
-   用户看到的数据不具备实时性
-   Research Engine 的评分结果无法在 UI 中体现

因此，本 Sprint 的核心任务是：

> 前端不再直接依赖本地 mock-data.ts，而是通过 API 获取数据。

------------------------------------------------------------------------

# 2. Sprint Objective

完成后：

-   Workspace 页面默认请求后端 API
-   Market Pulse 来自 `/api/v1/market/overview`
-   Hot Sectors 来自 `/api/v1/market/sectors`
-   Research Queue 来自 `/api/v1/research/queue`
-   Watchlist 来自 `/api/v1/watchlist`
-   AI Daily Brief 暂时可以仍为 mock 或后端生成模板
-   API 请求失败时才 fallback 到 mock 数据
-   页面保留 Loading / Error / Retry 状态

------------------------------------------------------------------------

# 3. Target Data Flow

``` text
Next.js Workspace Page
        │
        ▼
frontend/lib/api-client.ts
        │
        ▼
FastAPI Backend
        │
        ├── /api/v1/market/overview
        ├── /api/v1/market/sectors
        ├── /api/v1/research/queue
        └── /api/v1/watchlist
        │
        ▼
Application Service
        │
        ▼
Research Engine / Data Engine
        │
        ▼
Repository
        │
        ▼
Provider
```

------------------------------------------------------------------------

# 4. Frontend Requirements

## 4.1 Create API Client

新增：

``` text
frontend/lib/api-client.ts
```

示例：

``` ts
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function apiGet<T>(path: string, fallback?: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    if (fallback !== undefined) {
      console.warn("API failed, fallback to mock:", path, error);
      return fallback;
    }

    throw error;
  }
}
```

------------------------------------------------------------------------

## 4.2 Environment Variables

新增：

``` text
frontend/.env.local
```

内容：

``` env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
```

规则：

-   `NEXT_PUBLIC_USE_MOCK=true`：强制使用 mock
-   `NEXT_PUBLIC_USE_MOCK=false`：优先请求 API，失败 fallback mock

------------------------------------------------------------------------

## 4.3 Workspace Data Hook

新增：

``` text
frontend/hooks/useWorkspaceData.ts
```

职责：

-   请求 Market Pulse
-   请求 Hot Sectors
-   请求 Research Queue
-   请求 Watchlist
-   管理 loading
-   管理 error
-   提供 retry

建议返回：

``` ts
{
  marketPulse,
  hotSectors,
  researchQueue,
  watchlist,
  loading,
  error,
  retry,
  usingFallback
}
```

------------------------------------------------------------------------

# 5. Backend Requirements

如果后端接口还没统一，需要补齐：

## 5.1 Market API

``` text
GET /api/v1/market/overview
GET /api/v1/market/sectors
```

## 5.2 Research API

``` text
GET /api/v1/research/queue
GET /api/v1/research/score/{code}
```

## 5.3 Watchlist API

``` text
GET /api/v1/watchlist
POST /api/v1/watchlist
DELETE /api/v1/watchlist/{id}
```

第一阶段 Watchlist 可以先存在内存中，不需要数据库。

------------------------------------------------------------------------

# 6. Remove Direct Mock Dependency

以下组件禁止直接 import mock data：

-   MarketPulseCard
-   HotSectors
-   ResearchQueue
-   Watchlist
-   Workspace Page

允许：

-   `useWorkspaceData.ts` 中作为 fallback 使用 mock
-   开发模式下通过 `NEXT_PUBLIC_USE_MOCK=true` 强制 mock

------------------------------------------------------------------------

# 7. UI Changes

新增页面状态提示：

## API 正常

显示：

``` text
实时数据 · 后端已连接
```

## API 失败但 fallback mock

显示：

``` text
演示数据 · 后端连接失败 · 已使用本地备用数据
```

## 强制 mock

显示：

``` text
演示数据 · 当前为 Mock 模式
```

------------------------------------------------------------------------

# 8. CORS

FastAPI 必须允许前端访问：

``` python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

------------------------------------------------------------------------

# 9. Development Startup

要求 README 补充启动方式：

## Backend

``` bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Frontend

``` bash
cd frontend
npm install
npm run dev
```

访问：

``` text
http://localhost:3000
```

API 文档：

``` text
http://localhost:8000/docs
```

------------------------------------------------------------------------

# 10. Acceptance Criteria

完成后必须满足：

-   启动后端 `uvicorn app.main:app --reload --port 8000`
-   启动前端 `npm run dev`
-   打开 `http://localhost:3000`
-   Workspace 默认请求后端 API
-   Network 面板能看到 API 请求
-   后端关闭时页面 fallback 到 mock
-   页面显示当前数据模式 badge
-   组件不再直接 import mock-data
-   API 返回数据结构稳定
-   无控制台错误
-   无跨域错误
-   风险提示仍然保留

------------------------------------------------------------------------

# 11. Codex Tasks

请 Codex 执行：

``` text
请完成 Sprint 07：Replace Frontend Mock With Backend API。

要求：
1. 在 frontend/lib/ 中新增 api-client.ts。
2. 在 frontend/hooks/ 中新增 useWorkspaceData.ts。
3. Workspace 页面改为通过 useWorkspaceData 获取数据。
4. MarketPulseCard、HotSectors、ResearchQueue、Watchlist 不再直接 import mock-data。
5. 保留 mock-data 作为 fallback。
6. 新增 NEXT_PUBLIC_API_BASE_URL 和 NEXT_PUBLIC_USE_MOCK。
7. 根据数据来源显示不同 badge：
   - 实时数据 · 后端已连接
   - 演示数据 · 后端连接失败 · 已使用本地备用数据
   - 演示数据 · 当前为 Mock 模式
8. FastAPI 增加 CORS。
9. 确保后端提供 /api/v1/market/overview、/api/v1/market/sectors、/api/v1/research/queue、/api/v1/watchlist。
10. 更新 README 启动说明。
11. 确保前端和后端都能正常启动。
```

------------------------------------------------------------------------

# 12. Next Sprint

Sprint 08 --- Watchlist Persistence

目标：

-   引入数据库
-   Watchlist 持久化
-   用户本地观察池
-   Research Queue 与 Watchlist 联动
-   为后续用户系统做准备
