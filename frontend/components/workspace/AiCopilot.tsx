import { Bot, Send } from "lucide-react";

const prompts = ["今天应该研究什么？", "为什么机器人板块上涨？", "对比工业富联和中际旭创", "今天有哪些风险？"];

export function AiCopilot() {
  return (
    <aside className="border-l border-workspace-border bg-workspace-panel p-5">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-md bg-workspace-primary/20 text-workspace-primary">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-base font-bold">AI Research Copilot</h2>
          <p className="text-xs text-workspace-muted">研究伙伴，不直接给买卖指令。</p>
        </div>
      </div>

      <div className="mt-6 space-y-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            className="w-full rounded-md border border-workspace-border bg-workspace-card px-3 py-2 text-left text-sm text-workspace-muted hover:text-workspace-text"
            type="button"
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="mt-6 rounded-md border border-workspace-border bg-workspace-card p-4">
        <span className="text-xs font-bold uppercase tracking-[0.16em] text-workspace-primary">Draft Answer</span>
        <p className="mt-2 text-sm leading-6 text-workspace-muted">
          先看市场情绪是否延续，再看热点板块的龙头和趋势中军。当前只是 mock 演示，不连接真实 AI。
        </p>
      </div>

      <label className="mt-6 block">
        <span className="sr-only">Ask AI</span>
        <textarea
          className="h-28 w-full resize-none rounded-md border border-workspace-border bg-workspace-bg p-3 text-sm text-workspace-text outline-none placeholder:text-workspace-muted focus:border-workspace-primary"
          placeholder="输入你的研究问题..."
        />
      </label>
      <button className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-workspace-primary text-sm font-bold text-white" type="button">
        <Send className="h-4 w-4" />
        Send
      </button>
    </aside>
  );
}
