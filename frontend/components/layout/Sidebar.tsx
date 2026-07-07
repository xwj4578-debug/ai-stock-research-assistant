import { BarChart3, Bell, BriefcaseBusiness, FileText, Home, LineChart, Settings, Star } from "lucide-react";
import clsx from "clsx";

const navItems = [
  { label: "Workspace", icon: Home, active: true },
  { label: "Market", icon: BarChart3 },
  { label: "Sector", icon: LineChart },
  { label: "Stocks", icon: BriefcaseBusiness },
  { label: "Watchlist", icon: Star },
  { label: "Research Reports", icon: FileText },
  { label: "Review", icon: Bell },
  { label: "Settings", icon: Settings }
];

export function Sidebar() {
  return (
    <aside className="border-b border-workspace-border bg-workspace-panel px-3 py-3 xl:border-b-0 xl:border-r xl:py-4">
      <nav className="flex gap-2 overflow-x-auto xl:block xl:space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              type="button"
              className={clsx(
                "flex h-10 shrink-0 items-center gap-3 rounded-md px-3 text-left text-sm font-semibold transition xl:w-full",
                item.active
                  ? "bg-workspace-primary text-white shadow-[0_0_0_1px_rgba(79,139,255,0.35)]"
                  : "text-workspace-muted hover:bg-workspace-card hover:text-workspace-text"
              )}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
