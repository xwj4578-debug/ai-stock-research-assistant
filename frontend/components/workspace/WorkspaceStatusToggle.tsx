import { t } from "@/lib/i18n";

export type WorkspaceStatus = "normal" | "loading" | "empty" | "error";

type WorkspaceStatusToggleProps = {
  value: WorkspaceStatus;
  onChange: (value: WorkspaceStatus) => void;
};

const options: Array<{ value: WorkspaceStatus; label: string }> = [
  { value: "normal", label: t("status.normal") },
  { value: "loading", label: t("status.loading") },
  { value: "empty", label: t("status.empty") },
  { value: "error", label: t("status.error") }
];

export function WorkspaceStatusToggle({ value, onChange }: WorkspaceStatusToggleProps) {
  return (
    <div className="flex flex-wrap gap-2 rounded-md border border-workspace-border bg-workspace-card p-1">
      {options.map((item) => (
        <button
          key={item.value}
          className={`h-8 rounded px-3 text-xs font-bold ${
            value === item.value ? "bg-workspace-primary text-white" : "text-workspace-muted hover:text-workspace-text"
          }`}
          type="button"
          onClick={() => onChange(item.value)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
