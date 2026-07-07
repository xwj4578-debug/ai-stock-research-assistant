"use client";

import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { DailyBriefCard } from "@/components/workspace/DailyBriefCard";
import { EmptyState } from "@/components/workspace/EmptyState";
import { ErrorState } from "@/components/workspace/ErrorState";
import { HotSectors } from "@/components/workspace/HotSectors";
import { LoadingSkeleton } from "@/components/workspace/LoadingSkeleton";
import { MarketPulseCard } from "@/components/workspace/MarketPulseCard";
import { MockReportModal } from "@/components/workspace/MockReportModal";
import { ResearchQueue } from "@/components/workspace/ResearchQueue";
import { RiskAlerts } from "@/components/workspace/RiskAlerts";
import { SectorDetailModal } from "@/components/workspace/SectorDetailModal";
import { StockResearchDrawer } from "@/components/workspace/StockResearchDrawer";
import { Watchlist } from "@/components/workspace/Watchlist";
import { WorkspaceStatusToggle, type WorkspaceStatus } from "@/components/workspace/WorkspaceStatusToggle";
import { t } from "@/lib/i18n";
import { workspaceData } from "@/lib/mock-data";
import type { HotSector, ResearchQueueItem, WatchlistItem } from "@/types/workspace";

export function WorkspacePage() {
  const [status, setStatus] = useState<WorkspaceStatus>("normal");
  const [dailyBriefExpanded, setDailyBriefExpanded] = useState(false);
  const [selectedStock, setSelectedStock] = useState<ResearchQueueItem | null>(null);
  const [selectedSector, setSelectedSector] = useState<HotSector | null>(null);
  const [reportTitle, setReportTitle] = useState<string | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(workspaceData.watchlist);
  const [completedCodes, setCompletedCodes] = useState<string[]>([]);
  const [toast, setToast] = useState("");

  const sortedWatchlist = useMemo(
    () => watchlist.slice().sort((a, b) => Number(Boolean(b.pinned)) - Number(Boolean(a.pinned))),
    [watchlist]
  );

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 1800);
  }

  function addWatch(item: ResearchQueueItem) {
    if (watchlist.some((row) => row.code === item.code)) {
      showToast(t("toast.exists"));
      return;
    }
    setWatchlist((current) => [
      {
        code: item.code,
        name: item.name,
        score: item.score,
        risk: item.score >= 88 ? "Medium" : "Low",
        nextAction: item.nextStep || "继续观察"
      },
      ...current
    ]);
    showToast(t("toast.added"));
  }

  function toggleComplete(item: ResearchQueueItem) {
    setCompletedCodes((current) => (current.includes(item.code) ? current.filter((code) => code !== item.code) : [...current, item.code]));
    showToast(t("toast.completed"));
  }

  function pinWatch(item: WatchlistItem) {
    setWatchlist((current) => current.map((row) => (row.code === item.code ? { ...row, pinned: !row.pinned } : row)));
    showToast(t("toast.pinned"));
  }

  function deleteWatch(item: WatchlistItem) {
    setWatchlist((current) => current.filter((row) => row.code !== item.code));
    showToast(t("toast.deleted"));
  }

  return (
    <AppShell>
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-workspace-primary">{t("nav.workspace")}</span>
          <h1 className="mt-2 text-3xl font-black text-workspace-text">{t("workspace.title")}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-workspace-muted">{t("workspace.description")}</p>
        </div>
        <div className="flex flex-wrap justify-end gap-3">
          <WorkspaceStatusToggle value={status} onChange={setStatus} />
          <div className="rounded-md border border-workspace-border bg-workspace-card px-3 py-2 text-sm text-workspace-muted">{t("workspace.badge")}</div>
        </div>
      </div>

      {status === "loading" && <LoadingSkeleton />}
      {status === "empty" && <EmptyState title={t("workspace.emptyTitle")} description={t("workspace.emptyDescription")} />}
      {status === "error" && <ErrorState onRetry={() => setStatus("normal")} />}
      {status === "normal" && (
        <div className="space-y-5">
          <MarketPulseCard data={workspaceData.marketPulse} />
          <DailyBriefCard
            data={workspaceData.dailyBrief}
            expanded={dailyBriefExpanded}
            onToggle={() => setDailyBriefExpanded((value) => !value)}
            onGenerateReport={() => setReportTitle(t("dailyBrief.title"))}
          />
          <ResearchQueue
            items={workspaceData.researchQueue}
            completedCodes={completedCodes}
            onStartResearch={setSelectedStock}
            onAddWatch={addWatch}
            onToggleComplete={toggleComplete}
          />
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
            <div className="space-y-5">
              <HotSectors items={workspaceData.hotSectors} onOpen={setSelectedSector} />
              <Watchlist items={sortedWatchlist} onPin={pinWatch} onDelete={deleteWatch} onReport={(item) => setReportTitle(`${item.name} 研究报告`)} />
            </div>
            <RiskAlerts items={workspaceData.riskAlerts} />
          </div>
          <footer className="rounded-lg border border-workspace-border bg-workspace-panel p-3 text-xs leading-6 text-workspace-muted">
            {t("workspace.riskNotice")}
          </footer>
        </div>
      )}

      {toast && <div className="fixed bottom-5 left-1/2 z-[60] -translate-x-1/2 rounded-xl border border-workspace-border bg-workspace-card px-4 py-3 text-sm font-bold text-workspace-text shadow-terminal">{toast}</div>}
      <StockResearchDrawer stock={selectedStock} open={Boolean(selectedStock)} onClose={() => setSelectedStock(null)} />
      <SectorDetailModal sector={selectedSector} open={Boolean(selectedSector)} onClose={() => setSelectedSector(null)} />
      <MockReportModal open={Boolean(reportTitle)} title={reportTitle || undefined} onClose={() => setReportTitle(null)} />
    </AppShell>
  );
}
