import { AppShell } from "@/components/layout/AppShell";
import { DailyBriefCard } from "@/components/workspace/DailyBriefCard";
import { HotSectors } from "@/components/workspace/HotSectors";
import { MarketPulseCard } from "@/components/workspace/MarketPulseCard";
import { ResearchQueue } from "@/components/workspace/ResearchQueue";
import { RiskAlerts } from "@/components/workspace/RiskAlerts";
import { Watchlist } from "@/components/workspace/Watchlist";
import { workspaceData } from "@/lib/mock-data";

export default function Page() {
  return (
    <AppShell>
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-workspace-primary">Workspace</span>
          <h1 className="mt-2 text-3xl font-black text-workspace-text">今日研究工作台</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-workspace-muted">
            先判断市场，再选择板块，最后进入个股研究。页面使用 mock 数据，仅用于产品原型验证。
          </p>
        </div>
        <div className="rounded-md border border-workspace-border bg-workspace-card px-3 py-2 text-sm text-workspace-muted">
          Mock data · No backend · No real AI
        </div>
      </div>

      <div className="space-y-5">
        <MarketPulseCard data={workspaceData.marketPulse} />
        <DailyBriefCard data={workspaceData.dailyBrief} />
        <ResearchQueue items={workspaceData.researchQueue} />
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
          <div className="space-y-5">
            <HotSectors items={workspaceData.hotSectors} />
            <Watchlist items={workspaceData.watchlist} />
          </div>
          <RiskAlerts items={workspaceData.riskAlerts} />
        </div>
        <footer className="rounded-lg border border-workspace-border bg-workspace-panel p-4 text-sm leading-6 text-workspace-muted">
          风险提示：本产品仅用于投资研究和信息整理，不构成投资建议，不承诺收益，不替代用户独立判断。
        </footer>
      </div>
    </AppShell>
  );
}
