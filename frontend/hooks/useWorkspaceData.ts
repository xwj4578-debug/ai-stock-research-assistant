"use client";

import { useCallback, useEffect, useState } from "react";
import { apiGet, shouldForceMock } from "@/lib/api-client";
import { workspaceData } from "@/lib/mock-data";
import type { DailyBrief, HotSector, MarketPulse, ResearchQueueItem, WatchlistItem, WorkspaceData } from "@/types/workspace";

type DataMode = "api" | "fallback" | "mock";

type WatchlistResponse = {
  items: Array<{
    stockCode?: string;
    code?: string;
    name?: string;
    score?: number;
    riskLevel?: WatchlistItem["risk"];
    nextAction?: string;
  }>;
};

export function useWorkspaceData() {
  const [data, setData] = useState<WorkspaceData>(workspaceData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataMode, setDataMode] = useState<DataMode>(shouldForceMock() ? "mock" : "api");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    if (shouldForceMock()) {
      setData(workspaceData);
      setDataMode("mock");
      setLoading(false);
      return;
    }

    try {
      const [market, sectors, queue, watchlist] = await Promise.all([
        apiGet<MarketPulse>("/api/v1/market/overview", workspaceData.marketPulse),
        apiGet<HotSector[]>("/api/v1/market/sectors", workspaceData.hotSectors),
        apiGet<ResearchQueueItem[]>("/api/v1/research/queue", workspaceData.researchQueue),
        apiGet<WatchlistResponse>("/api/v1/watchlist", { items: workspaceData.watchlist.map((item) => ({ ...item, stockCode: item.code, riskLevel: item.risk })) })
      ]);
      const fallbackUsed = market.fallbackUsed || sectors.fallbackUsed || queue.fallbackUsed || watchlist.fallbackUsed;
      setData({
        marketPulse: market.data,
        dailyBrief: buildDailyBrief(market.data, sectors.data),
        hotSectors: sectors.data,
        researchQueue: queue.data,
        watchlist: normalizeWatchlist(watchlist.data),
        riskAlerts: buildRiskAlerts(queue.data)
      });
      setDataMode(fallbackUsed ? "fallback" : "api");
      setError(fallbackUsed ? "后端连接失败，已使用本地备用数据。" : null);
    } catch (err) {
      setData(workspaceData);
      setDataMode("fallback");
      setError(err instanceof Error ? err.message : "数据加载失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return {
    ...data,
    loading,
    error,
    retry: load,
    usingFallback: dataMode === "fallback",
    dataMode
  };
}

function normalizeWatchlist(response: WatchlistResponse): WatchlistItem[] {
  return (response.items || []).map((item) => ({
    code: item.stockCode || item.code || "",
    name: item.name || "待确认",
    score: item.score || 0,
    risk: item.riskLevel || "Medium",
    nextAction: item.nextAction || "继续观察"
  }));
}

function buildDailyBrief(market: MarketPulse, sectors: HotSector[]): DailyBrief {
  const names = sectors.slice(0, 3).map((item) => item.name).join("、") || "热点板块";
  return {
    title: "AI 市场日报",
    content: `${market.summary} 当前优先观察 ${names}。分数和排序来自后端 Research Engine，仅用于研究，不构成投资建议。`
  };
}

function buildRiskAlerts(queue: ResearchQueueItem[]) {
  const risks = queue
    .filter((item) => item.riskTip)
    .slice(0, 3)
    .map((item) => `${item.name}：${item.riskTip}`);
  return risks.length ? risks : workspaceData.riskAlerts;
}
