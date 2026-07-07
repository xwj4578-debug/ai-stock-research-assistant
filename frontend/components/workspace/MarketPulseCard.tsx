"use client";

import { Activity, ArrowDownRight, ArrowUpRight, Flame } from "lucide-react";
import { motion } from "framer-motion";
import type { MarketPulse } from "@/types/workspace";
import { t } from "@/lib/i18n";
import { marketColor } from "@/lib/market-color";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { Panel } from "@/components/workspace/Panel";

type MarketPulseCardProps = {
  data: MarketPulse;
};

function Metric({ label, value, tone = "neutral" }: { label: string; value: string | number; tone?: "neutral" | "up" | "down" }) {
  const color = tone === "up" ? marketColor.rise : tone === "down" ? marketColor.fall : "text-workspace-text";
  return (
    <div className="rounded-md border border-workspace-border bg-workspace-card p-3 transition hover:border-workspace-primary hover:bg-workspace-cardHover">
      <span className="block text-xs text-workspace-muted">{label}</span>
      <strong className={`mt-1 block text-base ${color}`}>{value}</strong>
    </div>
  );
}

export function MarketPulseCard({ data }: MarketPulseCardProps) {
  return (
    <Panel title={t("marketPulse.title")} eyebrow={t("marketPulse.eyebrow")}>
      <div className="grid gap-4 xl:grid-cols-[220px_minmax(0,1fr)]">
        <div className="rounded-lg border border-workspace-border bg-gradient-to-b from-[#1D2A45] to-workspace-card p-4">
          <div className="flex items-center gap-2 text-workspace-muted">
            <Activity className="h-4 w-4" />
            <span className="text-sm font-semibold">市场情绪</span>
          </div>
          <div className="mt-4 flex items-end gap-2">
            <AnimatedNumber value={data.score} className="text-6xl font-black leading-none text-workspace-text" />
            <span className={`pb-2 font-semibold ${marketColor.rise}`}>{data.status}</span>
          </div>
          <p className="mt-4 text-sm leading-6 text-workspace-muted">{data.summary}</p>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Metric label="成交额" value={data.turnover} />
          <Metric label="上涨家数" value={data.upCount} tone="up" />
          <Metric label="下跌家数" value={data.downCount} tone="down" />
          <Metric label="涨停 / 跌停" value={`${data.limitUp} / ${data.limitDown}`} tone="up" />
          <Metric label="炸板率" value={data.brokenRate} tone="down" />
          <Metric label="连板高度" value={data.leadingHeight} />
          <Metric label="强势信号" value="热点集中" tone="up" />
          <div className="rounded-md border border-workspace-border bg-workspace-card p-3 transition hover:border-workspace-primary hover:bg-workspace-cardHover">
            <span className="flex items-center gap-1 text-xs text-workspace-muted">
              <Flame className="h-3.5 w-3.5 text-workspace-warning" />
              情绪结构
            </span>
            <strong className="mt-1 flex items-center gap-1 text-base text-workspace-rise">
              <motion.span animate={{ y: [0, -2, 0] }} transition={{ duration: 1.2, repeat: Infinity, repeatDelay: 1.4 }}>
                <ArrowUpRight className="h-4 w-4" />
              </motion.span>
              情绪修复
            </strong>
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2 text-xs text-workspace-muted">
        <ArrowDownRight className="h-3.5 w-3.5 text-workspace-warning" />
        高位分歧仍需观察，风险提示优先于机会提示。
      </div>
    </Panel>
  );
}
