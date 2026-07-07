import { Plus, Search } from "lucide-react";
import type { ResearchQueueItem } from "@/types/workspace";
import { Panel } from "@/components/workspace/Panel";

type ResearchQueueProps = {
  items: ResearchQueueItem[];
};

export function ResearchQueue({ items }: ResearchQueueProps) {
  return (
    <Panel title="Research Queue" eyebrow="Must Review">
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item.code} className="grid gap-3 rounded-md border border-workspace-border bg-workspace-card p-4 xl:grid-cols-[minmax(0,1fr)_90px_210px] xl:items-center">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <strong>{item.name}</strong>
                <span className="rounded-full border border-workspace-border px-2 py-0.5 text-xs text-workspace-muted">{item.code}</span>
                <span className="rounded-full bg-workspace-primary/15 px-2 py-0.5 text-xs font-semibold text-workspace-primary">{item.status}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-workspace-muted">{item.reason}</p>
            </div>
            <div>
              <span className="block text-xs text-workspace-muted">综合评分</span>
              <strong className="text-2xl text-workspace-success">{item.score}</strong>
            </div>
            <div className="flex flex-wrap justify-end gap-2">
              <button className="inline-flex h-9 items-center gap-2 rounded-md bg-workspace-primary px-3 text-sm font-semibold text-white" type="button">
                <Search className="h-4 w-4" />
                开始研究
              </button>
              <button className="inline-flex h-9 items-center gap-2 rounded-md border border-workspace-border px-3 text-sm font-semibold text-workspace-muted" type="button">
                <Plus className="h-4 w-4" />
                加入观察池
              </button>
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
