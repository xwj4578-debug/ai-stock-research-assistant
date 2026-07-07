export function LoadingSkeleton() {
  return (
    <div className="space-y-5">
      {[0, 1, 2].map((item) => (
        <div key={item} className="rounded-lg border border-workspace-border bg-workspace-panel p-5">
          <div className="h-4 w-36 animate-pulse rounded-full bg-workspace-card" />
          <div className="mt-5 grid gap-3 md:grid-cols-4">
            <div className="h-24 animate-pulse rounded-md bg-workspace-card" />
            <div className="h-24 animate-pulse rounded-md bg-workspace-card" />
            <div className="h-24 animate-pulse rounded-md bg-workspace-card" />
            <div className="h-24 animate-pulse rounded-md bg-workspace-card" />
          </div>
        </div>
      ))}
    </div>
  );
}
