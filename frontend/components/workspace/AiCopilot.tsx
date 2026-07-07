"use client";

import { type KeyboardEvent, useState } from "react";
import { Bot, Send } from "lucide-react";
import { getMockAiAnswer } from "@/lib/mock-ai";
import { t } from "@/lib/i18n";

const prompts = ["今天应该研究什么？", "为什么机器人板块上涨？", "对比工业富联和中际旭创", "今天有哪些风险？"];

type Message = {
  role: "user" | "ai";
  text: string;
};

export function AiCopilot() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "ai",
      text: "先看市场情绪是否延续，再看热点板块的龙头和趋势中军。当前只是模拟演示，不连接真实 AI。"
    }
  ]);

  function ask(question: string) {
    if (!question.trim() || loading) return;
    setInput(question);
    setMessages((current) => [...current, { role: "user", text: question }]);
    setLoading(true);
    window.setTimeout(() => {
      setMessages((current) => [...current, { role: "ai", text: getMockAiAnswer(question) }]);
      setLoading(false);
      setInput("");
    }, 600);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    ask(input);
  }

  return (
    <aside className="flex max-h-[calc(100vh-64px)] flex-col border-l border-workspace-border bg-workspace-panel p-5">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-md bg-workspace-primary/20 text-workspace-primary">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-base font-bold">{t("copilot.title")}</h2>
          <p className="text-xs text-workspace-muted">{t("copilot.description")}</p>
        </div>
      </div>

      <div className="mt-5 grid gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            className="min-h-10 rounded-md border border-workspace-border bg-workspace-card px-3 py-2 text-left text-sm text-workspace-muted transition hover:text-workspace-text active:scale-[0.99]"
            type="button"
            onClick={() => ask(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="mt-5 min-h-0 flex-1 space-y-3 overflow-y-auto rounded-md border border-workspace-border bg-workspace-card p-3">
        <span className="text-xs font-bold uppercase tracking-[0.16em] text-workspace-primary">{t("copilot.analysis")}</span>
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[88%] whitespace-pre-line rounded-md p-3 text-sm leading-6 ${message.role === "ai" ? "bg-workspace-bg text-workspace-muted" : "bg-workspace-primary text-white"}`}>
              {message.text}
            </div>
          </div>
        ))}
        {loading && <div className="rounded-md bg-workspace-bg p-3 text-sm text-workspace-muted">AI 正在生成模拟回复...</div>}
      </div>

      <div className="mt-4">
        <textarea
          className="h-24 w-full resize-none rounded-md border border-workspace-border bg-workspace-bg p-3 text-sm text-workspace-text outline-none placeholder:text-workspace-muted focus:border-workspace-primary"
          placeholder={t("copilot.placeholder")}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-workspace-primary text-sm font-bold text-white hover:brightness-110 active:scale-[0.98]" type="button" onClick={() => ask(input)}>
          <Send className="h-4 w-4" />
          {t("copilot.send")}
        </button>
        <p className="mt-2 text-xs text-workspace-muted">{t("copilot.mockNote")}</p>
      </div>
    </aside>
  );
}
