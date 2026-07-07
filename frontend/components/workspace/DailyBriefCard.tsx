import type { DailyBrief } from "@/types/workspace";
import { t } from "@/lib/i18n";
import { Panel } from "@/components/workspace/Panel";

type DailyBriefCardProps = {
  data: DailyBrief;
  expanded: boolean;
  onToggle: () => void;
  onGenerateReport: () => void;
};

export function DailyBriefCard({ data, expanded, onToggle, onGenerateReport }: DailyBriefCardProps) {
  const shortText = data.content.length > 66 ? `${data.content.slice(0, 66)}...` : data.content;

  return (
    <Panel
      title={t("dailyBrief.title")}
      eyebrow={t("dailyBrief.eyebrow")}
      action={
        <div className="flex gap-2">
          <button className="h-9 rounded-md border border-workspace-border px-3 text-sm font-semibold text-workspace-muted hover:text-workspace-text active:scale-[0.98]" type="button" onClick={onToggle}>
            {expanded ? t("dailyBrief.collapse") : t("dailyBrief.expand")}
          </button>
          <button className="h-9 rounded-md bg-workspace-primary px-3 text-sm font-semibold text-white hover:brightness-110 active:scale-[0.98]" type="button" onClick={onGenerateReport}>
            {t("dailyBrief.report")}
          </button>
        </div>
      }
    >
      <p className="text-sm leading-7 text-workspace-text">{expanded ? data.content : shortText}</p>
    </Panel>
  );
}
