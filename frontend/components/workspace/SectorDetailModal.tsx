import { X } from "lucide-react";
import type { HotSector } from "@/types/workspace";
import { t } from "@/lib/i18n";

type SectorDetailModalProps = {
  sector: HotSector | null;
  open: boolean;
  onClose: () => void;
};

export function SectorDetailModal({ sector, open, onClose }: SectorDetailModalProps) {
  if (!open || !sector) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/55 p-4" role="dialog" aria-modal="true">
      <section className="w-full max-w-3xl rounded-lg border border-workspace-border bg-workspace-panel shadow-terminal">
        <header className="flex items-start justify-between gap-4 border-b border-workspace-border p-5">
          <div>
            <span className="text-xs font-bold text-workspace-primary">{t("modal.sectorTitle")}</span>
            <h2 className="mt-2 text-2xl font-black">{sector.name}</h2>
            <p className="mt-1 text-sm text-workspace-success">{sector.change} · 热度 {sector.score}</p>
          </div>
          <button className="grid h-9 w-9 place-items-center rounded-md border border-workspace-border text-workspace-muted" type="button" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="grid gap-4 p-5 md:grid-cols-2">
          <Metric label="龙头股" value={sector.leader} />
          <Metric label="趋势中军" value={sector.trendCore || "待观察"} />
          <Metric label="补涨股" value={sector.reboundStock || "待观察"} />
          <Metric label="主要风险" value={sector.risk || "高位分歧"} danger />
          <div className="md:col-span-2 rounded-lg border border-workspace-border bg-workspace-card p-4">
            <h3 className="text-sm font-bold">AI 板块总结</h3>
            <p className="mt-2 text-sm leading-6 text-workspace-muted">{sector.reason}</p>
          </div>
          <div className="md:col-span-2 flex flex-wrap gap-2">
            {(sector.relatedStocks || []).map((item) => (
              <span key={item} className="rounded-full border border-workspace-border bg-workspace-card px-3 py-1 text-sm text-workspace-muted">
                {item}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value, danger = false }: { label: string; value: string; danger?: boolean }) {
  return (
    <div className="rounded-lg border border-workspace-border bg-workspace-card p-4">
      <span className="text-xs text-workspace-muted">{label}</span>
      <strong className={`mt-1 block text-base ${danger ? "text-workspace-danger" : "text-workspace-text"}`}>{value}</strong>
    </div>
  );
}
