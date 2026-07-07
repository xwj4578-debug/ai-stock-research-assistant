import { X } from "lucide-react";
import { t } from "@/lib/i18n";

type MockReportModalProps = {
  open: boolean;
  title?: string;
  onClose: () => void;
};

export function MockReportModal({ open, title = "AI 长报告", onClose }: MockReportModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/55 p-4" role="dialog" aria-modal="true">
      <section className="w-full max-w-2xl rounded-lg border border-workspace-border bg-workspace-panel shadow-terminal">
        <header className="flex items-center justify-between border-b border-workspace-border p-5">
          <div>
            <span className="text-xs font-bold text-workspace-primary">{t("modal.reportTitle")}</span>
            <h2 className="mt-2 text-xl font-black">{title}</h2>
          </div>
          <button className="grid h-9 w-9 place-items-center rounded-md border border-workspace-border text-workspace-muted" type="button" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </button>
        </header>
        <div className="space-y-4 p-5 text-sm leading-7 text-workspace-muted">
          <p>今日市场情绪偏强，热点集中在机器人、AI 算力和半导体方向。研究顺序建议从板块强度开始，再筛选趋势中军。</p>
          <p>机会侧重点：优先看有容量、有承接、有产业逻辑的个股。风险侧重点：高位连板分歧、短线涨幅过大和热点轮动过快。</p>
          <p>本报告为 mock 演示，不包含真实行情、真实 AI 推理或投资建议。</p>
        </div>
      </section>
    </div>
  );
}
