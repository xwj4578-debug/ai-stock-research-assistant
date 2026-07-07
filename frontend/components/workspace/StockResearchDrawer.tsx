import { X } from "lucide-react";
import type { ResearchQueueItem } from "@/types/workspace";
import { t } from "@/lib/i18n";

type StockResearchDrawerProps = {
  stock: ResearchQueueItem | null;
  open: boolean;
  onClose: () => void;
};

export function StockResearchDrawer({ stock, open, onClose }: StockResearchDrawerProps) {
  if (!open || !stock) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50" role="dialog" aria-modal="true">
      <aside className="ml-auto flex h-full w-full max-w-xl flex-col border-l border-workspace-border bg-workspace-panel shadow-terminal">
        <header className="flex items-start justify-between gap-4 border-b border-workspace-border p-5">
          <div>
            <span className="text-xs font-bold text-workspace-primary">{t("drawer.title")}</span>
            <h2 className="mt-2 text-2xl font-black">{stock.name}</h2>
            <p className="mt-1 text-sm text-workspace-muted">{stock.code} · {stock.sector || "板块待确认"}</p>
          </div>
          <button className="grid h-9 w-9 place-items-center rounded-md border border-workspace-border text-workspace-muted" type="button" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          <div className="rounded-lg border border-workspace-border bg-workspace-card p-4">
            <span className="text-xs text-workspace-muted">{t("drawer.score")}</span>
            <strong className="mt-1 block text-4xl text-workspace-success">{stock.score}</strong>
          </div>
          <InfoBlock title="AI 核心结论" text={stock.conclusion || stock.reason} />
          <InfoBlock title="上涨逻辑" text={stock.riseLogic || "板块热度提升和资金关注带来短线修复。"} />
          <InfoBlock title="风险提示" text={stock.riskTip || "高位不追，先看回踩承接。"} danger />
          <InfoBlock title="下一步建议" text={stock.nextStep || "加入观察池，等待位置和资金确认。"} />
        </div>
      </aside>
    </div>
  );
}

function InfoBlock({ title, text, danger = false }: { title: string; text: string; danger?: boolean }) {
  return (
    <section className={`rounded-lg border p-4 ${danger ? "border-workspace-danger/30 bg-workspace-danger/10" : "border-workspace-border bg-workspace-card"}`}>
      <h3 className="text-sm font-bold text-workspace-text">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-workspace-muted">{text}</p>
    </section>
  );
}
