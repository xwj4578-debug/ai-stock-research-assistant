import type { ReactNode } from "react";

type PanelProps = {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function Panel({ title, eyebrow, action, children, className = "" }: PanelProps) {
  return (
    <section className={`rounded-lg border border-workspace-border bg-workspace-panel p-5 shadow-terminal ${className}`}>
      {(title || eyebrow || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {eyebrow && <span className="text-xs font-bold uppercase tracking-[0.16em] text-workspace-primary">{eyebrow}</span>}
            {title && <h2 className="mt-1 text-lg font-bold text-workspace-text">{title}</h2>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
