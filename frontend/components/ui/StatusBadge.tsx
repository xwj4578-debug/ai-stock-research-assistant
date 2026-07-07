import type { ReactNode } from "react";

type StatusBadgeProps = {
  children: ReactNode;
  tone?: "default" | "primary" | "success" | "warning" | "danger" | "ai";
};

const toneClass = {
  default: "border-workspace-border text-workspace-muted",
  primary: "border-workspace-primary/40 bg-workspace-primary/10 text-workspace-primary",
  success: "border-workspace-rise/40 bg-workspace-rise/10 text-workspace-rise",
  warning: "border-workspace-warning/40 bg-workspace-warning/10 text-workspace-warning",
  danger: "border-workspace-danger/40 bg-workspace-danger/10 text-workspace-danger",
  ai: "border-workspace-ai/40 bg-workspace-ai/10 text-workspace-ai"
};

export function StatusBadge({ children, tone = "default" }: StatusBadgeProps) {
  return <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${toneClass[tone]}`}>{children}</span>;
}
