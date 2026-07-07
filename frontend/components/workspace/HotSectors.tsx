"use client";

import { motion } from "framer-motion";
import type { HotSector } from "@/types/workspace";
import { t } from "@/lib/i18n";
import { marketColor } from "@/lib/market-color";
import { itemMotion, listMotion } from "@/lib/motion";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Panel } from "@/components/workspace/Panel";

type HotSectorsProps = {
  items: HotSector[];
  onOpen: (item: HotSector) => void;
};

export function HotSectors({ items, onOpen }: HotSectorsProps) {
  return (
    <Panel title={t("hotSectors.title")} eyebrow={t("hotSectors.eyebrow")}>
      <motion.div {...listMotion} className="grid gap-3">
        {items.map((item) => (
          <motion.button
            {...itemMotion}
            whileTap={{ scale: 0.99 }}
            key={item.name}
            className="rounded-md border border-workspace-border bg-workspace-card p-4 text-left transition hover:border-workspace-primary hover:bg-workspace-cardHover"
            type="button"
            onClick={() => onOpen(item)}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <strong>{item.name}</strong>
                <p className="mt-2 text-sm leading-6 text-workspace-muted">{item.reason}</p>
              </div>
              <span className={`text-sm font-bold ${marketColor.rise}`}>{item.change}</span>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
              <StatusBadge tone="warning">热度 {item.score}</StatusBadge>
              <StatusBadge>龙头 {item.leader}</StatusBadge>
            </div>
          </motion.button>
        ))}
      </motion.div>
    </Panel>
  );
}
