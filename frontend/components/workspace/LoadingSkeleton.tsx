export function LoadingSkeleton() {
  return (
    <div className="space-y-5">
      {[0, 1, 2].map((item) => (
        <div key={item} className="rounded-lg border border-workspace-border bg-workspace-panel p-5">
          <div className="skeleton-shimmer h-4 w-36 rounded-full bg-workspace-card" />
          <div className="mt-5 grid gap-3 md:grid-cols-4">
            <div className="skeleton-shimmer h-24 rounded-md bg-workspace-card" />
            <div className="skeleton-shimmer h-24 rounded-md bg-workspace-card" />
            <div className="skeleton-shimmer h-24 rounded-md bg-workspace-card" />
            <div className="skeleton-shimmer h-24 rounded-md bg-workspace-card" />
          </div>
        </div>
      ))}
    </div>
  );
}
