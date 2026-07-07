import { Inbox } from "lucide-react";

type EmptyStateProps = {
  title: string;
  description: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-workspace-border bg-workspace-card p-8 text-center">
      <Inbox className="mx-auto h-8 w-8 text-workspace-muted" />
      <h3 className="mt-3 text-base font-bold text-workspace-text">{title}</h3>
      <p className="mt-2 text-sm text-workspace-muted">{description}</p>
    </div>
  );
}
