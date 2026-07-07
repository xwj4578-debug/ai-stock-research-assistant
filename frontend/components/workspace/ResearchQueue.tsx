import { Plus, Search } from "lucide-react";
import type { ResearchQueueItem } from "@/types/workspace";
import { t } from "@/lib/i18n";
import { Panel } from "@/components/workspace/Panel";

type ResearchQueueProps = {
  items: ResearchQueueItem[];
  completedCodes: string[];
  onStartResearch: (item: ResearchQueueItem) => void;
  onAddWatch: (item: ResearchQueueItem) => void;
  onToggleComplete: (item: ResearchQueueItem) => void;
};

export function ResearchQueue({ items, completedCodes, onStartResearch, onAddWatch, onToggleComplete }: ResearchQueueProps) {
  return (
    <Panel title={t("researchQueue.title")} eyebrow={t("researchQueue.eyebrow")}>
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item.code} className={`grid min-h-24 gap-3 rounded-xl border border-workspace-border bg-workspace-card p-3 transition hover:border-workspace-primary hover:bg-workspace-cardHover xl:grid-cols-[minmax(0,1fr)_78px_300px] xl:items-center ${completedCodes.includes(item.code) ? "opacity-50" : ""}`}>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <strong>{item.name}</strong>
                <span className="rounded-full border border-workspace-border px-2 py-0.5 text-xs text-workspace-muted">{item.code}</span>
                <span className="rounded-full bg-workspace-primary/15 px-2 py-0.5 text-xs font-semibold text-workspace-primary">{completedCodes.includes(item.code) ? "已完成" : item.status}</span>
              </div>
              <p className="line-clamp-2 mt-2 text-sm leading-6 text-workspace-muted">{item.reason}</p>
            </div>
            <div>
              <span className="block text-xs text-workspace-muted">{t("researchQueue.score")}</span>
              <strong className="text-2xl text-workspace-rise">{item.score}</strong>
            </div>
            <div className="flex flex-wrap justify-end gap-2">
              <button className="inline-flex h-9 items-center gap-2 rounded-md bg-workspace-primary px-3 text-sm font-semibold text-white hover:brightness-110 active:scale-[0.98]" type="button" onClick={() => onStartResearch(item)}>
                <Search className="h-4 w-4" />
                {t("researchQueue.start")}
              </button>
              <button className="inline-flex h-9 items-center gap-2 rounded-md border border-workspace-border px-3 text-sm font-semibold text-workspace-muted hover:text-workspace-text active:scale-[0.98]" type="button" onClick={() => onAddWatch(item)}>
                <Plus className="h-4 w-4" />
                {t("researchQueue.addWatch")}
              </button>
              <button className="h-9 rounded-md border border-workspace-border px-3 text-sm font-semibold text-workspace-muted hover:text-workspace-text active:scale-[0.98]" type="button" onClick={() => onToggleComplete(item)}>
                {completedCodes.includes(item.code) ? t("researchQueue.restore") : t("researchQueue.complete")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
