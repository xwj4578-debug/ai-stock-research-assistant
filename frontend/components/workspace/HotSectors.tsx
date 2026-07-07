import type { HotSector } from "@/types/workspace";
import { Panel } from "@/components/workspace/Panel";

type HotSectorsProps = {
  items: HotSector[];
};

export function HotSectors({ items }: HotSectorsProps) {
  return (
    <Panel title="Hot Sectors" eyebrow="Market Direction">
      <div className="grid gap-3">
        {items.map((item) => (
          <article key={item.name} className="rounded-md border border-workspace-border bg-workspace-card p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <strong>{item.name}</strong>
                <p className="mt-2 text-sm leading-6 text-workspace-muted">{item.reason}</p>
              </div>
              <span className="text-sm font-bold text-workspace-success">{item.change}</span>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded-full border border-workspace-border px-2 py-1 text-workspace-muted">热度 {item.score}</span>
              <span className="rounded-full border border-workspace-border px-2 py-1 text-workspace-muted">龙头 {item.leader}</span>
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
