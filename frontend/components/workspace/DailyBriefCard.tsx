import type { DailyBrief } from "@/types/workspace";
import { Panel } from "@/components/workspace/Panel";

type DailyBriefCardProps = {
  data: DailyBrief;
};

export function DailyBriefCard({ data }: DailyBriefCardProps) {
  return (
    <Panel
      title={data.title}
      eyebrow="AI Summary"
      action={
        <div className="flex gap-2">
          <button className="h-9 rounded-md border border-workspace-border px-3 text-sm font-semibold text-workspace-muted" type="button">
            展开全文
          </button>
          <button className="h-9 rounded-md bg-workspace-primary px-3 text-sm font-semibold text-white" type="button">
            生成长报告
          </button>
        </div>
      }
    >
      <p className="text-sm leading-7 text-workspace-text">{data.content}</p>
    </Panel>
  );
}
