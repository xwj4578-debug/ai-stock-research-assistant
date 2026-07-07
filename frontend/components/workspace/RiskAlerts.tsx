import { AlertTriangle } from "lucide-react";
import { t } from "@/lib/i18n";
import { Panel } from "@/components/workspace/Panel";

type RiskAlertsProps = {
  items: string[];
};

export function RiskAlerts({ items }: RiskAlertsProps) {
  return (
    <Panel title={t("riskAlerts.title")} eyebrow={t("riskAlerts.eyebrow")}>
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item} className="flex gap-3 rounded-md border border-workspace-danger/30 bg-workspace-danger/10 p-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 flex-none text-workspace-warning" />
            <p className="text-sm leading-6 text-workspace-text">{item}</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
