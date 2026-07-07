import clsx from "clsx";
import type { WatchlistItem } from "@/types/workspace";
import { t } from "@/lib/i18n";
import { EmptyState } from "@/components/workspace/EmptyState";
import { Panel } from "@/components/workspace/Panel";

type WatchlistProps = {
  items: WatchlistItem[];
  onPin: (item: WatchlistItem) => void;
  onDelete: (item: WatchlistItem) => void;
  onReport: (item: WatchlistItem) => void;
};

const riskClass: Record<WatchlistItem["risk"], string> = {
  Low: "text-workspace-success",
  Medium: "text-workspace-warning",
  High: "text-workspace-danger"
};

export function Watchlist({ items, onPin, onDelete, onReport }: WatchlistProps) {
  return (
    <Panel title={t("watchlist.title")} eyebrow={t("watchlist.eyebrow")}>
      {!items.length && <EmptyState title={t("watchlist.emptyTitle")} description={t("watchlist.emptyDescription")} />}
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item.code} className="rounded-md border border-workspace-border bg-workspace-card p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <strong>{item.name}</strong>
                <span className="ml-2 text-xs text-workspace-muted">{item.code}</span>
              </div>
              <strong className="text-workspace-success">{item.score}</strong>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className={clsx("rounded-full border border-workspace-border px-2 py-1 font-semibold", riskClass[item.risk])}>
                Risk {item.risk}
              </span>
              <span className="rounded-full border border-workspace-border px-2 py-1 text-workspace-muted">{item.nextAction}</span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="h-8 rounded-md border border-workspace-border px-3 text-xs font-bold text-workspace-muted hover:text-workspace-text" type="button" onClick={() => onPin(item)}>
                {item.pinned ? t("watchlist.unpin") : t("watchlist.pin")}
              </button>
              <button className="h-8 rounded-md border border-workspace-border px-3 text-xs font-bold text-workspace-muted hover:text-workspace-text" type="button" onClick={() => onReport(item)}>
                {t("watchlist.report")}
              </button>
              <button className="h-8 rounded-md border border-workspace-danger/40 px-3 text-xs font-bold text-workspace-danger hover:bg-workspace-danger/10" type="button" onClick={() => onDelete(item)}>
                {t("watchlist.delete")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
