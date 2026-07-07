import clsx from "clsx";
import type { WatchlistItem } from "@/types/workspace";
import { Panel } from "@/components/workspace/Panel";

type WatchlistProps = {
  items: WatchlistItem[];
};

const riskClass: Record<WatchlistItem["risk"], string> = {
  Low: "text-workspace-success",
  Medium: "text-workspace-warning",
  High: "text-workspace-danger"
};

export function Watchlist({ items }: WatchlistProps) {
  return (
    <Panel title="Watchlist" eyebrow="Track Next">
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
          </article>
        ))}
      </div>
    </Panel>
  );
}
