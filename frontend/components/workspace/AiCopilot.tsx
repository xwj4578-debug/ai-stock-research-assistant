"use client";

import { AnimatePresence, motion } from "framer-motion";
import { type KeyboardEvent, useEffect, useMemo, useState } from "react";
import { Bot, Loader2, Send } from "lucide-react";
import { getMockAiAnswer } from "@/lib/mock-ai";
import { itemMotion, listMotion, motionTimings } from "@/lib/motion";
import { t } from "@/lib/i18n";

const prompts = ["今天应该研究什么？", "机器人为什么上涨？", "对比工业富联和中际旭创", "今天有哪些风险？"];

type Message = {
  id: string;
  role: "user" | "ai";
  text: string;
};

function TypewriterText({ text, active }: { text: string; active: boolean }) {
  const [visibleText, setVisibleText] = useState(active ? "" : text);

  useEffect(() => {
    if (!active) {
      setVisibleText(text);
      return;
    }

    setVisibleText("");
    let index = 0;
    const timer = window.setInterval(() => {
      index += 1;
      setVisibleText(text.slice(0, index));
      if (index >= text.length) {
        window.clearInterval(timer);
      }
    }, 18);

    return () => window.clearInterval(timer);
  }, [active, text]);

  return <>{visibleText}</>;
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 text-workspace-muted">
      {[0, 1, 2].map((dot) => (
        <motion.span
          key={dot}
          className="h-1.5 w-1.5 rounded-full bg-workspace-primary"
          animate={{ opacity: [0.35, 1, 0.35], y: [0, -3, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: dot * 0.12, ease: "easeInOut" }}
        />
      ))}
      <span className="ml-1 text-xs">正在生成模拟回答</span>
    </div>
  );
}

export function AiCopilot() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "ai",
      text: "先看市场情绪是否延续，再看热点板块的龙头和趋势中军。当前是模拟演示，不连接真实 AI。"
    }
  ]);
  const latestAiMessageId = useMemo(() => [...messages].reverse().find((message) => message.role === "ai")?.id, [messages]);

  function ask(question: string) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const timestamp = Date.now();
    setMessages((current) => [...current, { id: `user-${timestamp}`, role: "user", text: trimmed }]);
    setLoading(true);

    window.setTimeout(() => {
      setMessages((current) => [...current, { id: `ai-${timestamp}`, role: "ai", text: getMockAiAnswer(trimmed) }]);
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
        <motion.div
          className="grid h-10 w-10 place-items-center rounded-md bg-workspace-primary/20 text-workspace-primary"
          animate={{ boxShadow: ["0 0 0 rgba(45, 127, 249, 0)", "0 0 24px rgba(45, 127, 249, 0.22)", "0 0 0 rgba(45, 127, 249, 0)"] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        >
          <Bot className="h-5 w-5" />
        </motion.div>
        <div>
          <h2 className="text-base font-bold">{t("copilot.title")}</h2>
          <p className="text-xs text-workspace-muted">{t("copilot.description")}</p>
        </div>
      </div>

      <motion.div className="mt-5 grid gap-2" {...listMotion}>
        {prompts.map((prompt) => (
          <motion.button
            key={prompt}
            {...itemMotion}
            className="min-h-10 rounded-md border border-workspace-border bg-workspace-card px-3 py-2 text-left text-sm text-workspace-muted transition hover:text-workspace-text active:scale-[0.99]"
            type="button"
            onClick={() => ask(prompt)}
            whileHover={{ x: 2 }}
            whileTap={{ scale: 0.98 }}
          >
            {prompt}
          </motion.button>
        ))}
      </motion.div>

      <div className="mt-5 min-h-0 flex-1 space-y-3 overflow-y-auto rounded-md border border-workspace-border bg-workspace-card p-3">
        <span className="text-xs font-bold uppercase tracking-[0.16em] text-workspace-primary">{t("copilot.analysis")}</span>
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              initial={{ opacity: 0, y: 8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.98 }}
              transition={{ duration: motionTimings.normal, ease: "easeOut" }}
            >
              <div className={`max-w-[88%] whitespace-pre-line rounded-md p-3 text-sm leading-6 ${message.role === "ai" ? "bg-workspace-bg text-workspace-muted" : "bg-workspace-primary text-white"}`}>
                <TypewriterText text={message.text} active={message.role === "ai" && message.id === latestAiMessageId && message.id !== "welcome"} />
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div
              key="loading"
              className="rounded-md bg-workspace-bg p-3 text-sm"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
            >
              <LoadingDots />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-4">
        <textarea
          className="h-24 w-full resize-none rounded-md border border-workspace-border bg-workspace-bg p-3 text-sm text-workspace-text outline-none placeholder:text-workspace-muted focus:border-workspace-primary"
          placeholder={t("copilot.placeholder")}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <motion.button
          className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-workspace-primary text-sm font-bold text-white hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          type="button"
          onClick={() => ask(input)}
          disabled={loading || !input.trim()}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          {t("copilot.send")}
        </motion.button>
        <p className="mt-2 text-xs text-workspace-muted">{t("copilot.mockNote")}</p>
      </div>
    </aside>
  );
}
