import type { ReactNode } from "react";
import { AiCopilot } from "@/components/workspace/AiCopilot";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-workspace-bg text-workspace-text">
      <Topbar />
      <div className="grid min-h-[calc(100vh-64px)] grid-cols-1 xl:grid-cols-[240px_minmax(0,1fr)_360px]">
        <Sidebar />
        <main className="min-w-0 overflow-y-auto px-6 py-5">{children}</main>
        <AiCopilot />
      </div>
    </div>
  );
}
