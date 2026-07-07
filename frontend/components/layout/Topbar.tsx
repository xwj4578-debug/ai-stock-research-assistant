import { Bell, Search, UserCircle } from "lucide-react";

export function Topbar() {
  return (
    <header className="grid min-h-16 gap-3 border-b border-workspace-border bg-workspace-panel px-4 py-3 lg:grid-cols-[240px_minmax(0,1fr)_auto] lg:items-center lg:px-5">
      <div className="flex items-center gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-md bg-workspace-primary text-sm font-black text-white">
          A
        </div>
        <div>
          <strong className="block text-sm">AlphaLens</strong>
          <span className="text-xs text-workspace-muted">Research Workspace</span>
        </div>
      </div>

      <label className="relative block max-w-3xl">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-workspace-muted" />
        <span className="sr-only">Search</span>
        <input
          className="h-10 w-full rounded-md border border-workspace-border bg-workspace-bg pl-10 pr-4 text-sm text-workspace-text outline-none transition placeholder:text-workspace-muted focus:border-workspace-primary"
          placeholder="搜索股票 / 板块 / 问 AI"
        />
      </label>

      <div className="flex items-center gap-2 pl-4">
        <button className="grid h-10 w-10 place-items-center rounded-md border border-workspace-border text-workspace-muted hover:text-workspace-text" type="button" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </button>
        <button className="grid h-10 w-10 place-items-center rounded-md border border-workspace-border text-workspace-muted hover:text-workspace-text" type="button" aria-label="Profile">
          <UserCircle className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
