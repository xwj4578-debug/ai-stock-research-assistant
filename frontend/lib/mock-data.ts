import type { WorkspaceData } from "@/types/workspace";

export const workspaceData: WorkspaceData = {
  marketPulse: {
    score: 78,
    status: "偏强",
    turnover: "1.28 万亿",
    upCount: 3621,
    downCount: 1587,
    limitUp: 86,
    limitDown: 9,
    brokenRate: "18%",
    leadingHeight: "5 连板",
    summary: "今日市场情绪偏强，机器人、AI 算力和半导体方向表现活跃。"
  },
  dailyBrief: {
    title: "AI Daily Brief",
    content:
      "今日市场情绪回暖，资金主要集中在机器人、AI 算力和半导体方向。短线情绪有所修复，但高位股分歧仍然明显，建议优先研究热点板块中的趋势中军，不追后排。"
  },
  researchQueue: [
    {
      code: "601138",
      name: "工业富联",
      score: 91,
      status: "待研究",
      reason: "AI 服务器与算力产业链核心标的，资金持续关注。",
      sector: "AI 算力",
      conclusion: "算力主线容量中军，适合先做研究跟踪。",
      riseLogic: "AI 服务器需求预期提升，带动资金关注核心供应链。",
      riskTip: "短线涨幅较大时不要追高，重点看回踩承接。",
      nextStep: "等待回踩 5 日线后再观察资金是否继续流入。"
    },
    {
      code: "300308",
      name: "中际旭创",
      score: 88,
      status: "跟踪中",
      reason: "CPO 方向趋势中军，机构关注度较高。",
      sector: "AI 算力",
      conclusion: "弹性更高，波动也更大，适合和工业富联对比研究。",
      riseLogic: "CPO 景气度预期改善，带动光模块方向走强。",
      riskTip: "估值和波动都偏高，避免情绪高点追入。",
      nextStep: "观察放量突破后能否缩量回踩不破。"
    },
    {
      code: "002156",
      name: "通富微电",
      score: 84,
      status: "待研究",
      reason: "半导体封测方向活跃，板块热度提升。",
      sector: "半导体",
      conclusion: "半导体封测方向代表，适合观察板块轮动持续性。",
      riseLogic: "国产替代和封测景气预期改善推动板块修复。",
      riskTip: "板块轮动快，若放量不持续容易回落。",
      nextStep: "先看半导体板块热度能否维持。"
    }
  ],
  hotSectors: [
    {
      name: "机器人",
      change: "+4.82%",
      score: 92,
      leader: "巨轮智能",
      reason: "政策催化叠加产业消息发酵，板块涨停家数较多。",
      trendCore: "汇川技术",
      reboundStock: "埃斯顿",
      risk: "高位连板分歧加大，后排不适合追。",
      relatedStocks: ["巨轮智能", "汇川技术", "埃斯顿", "机器人"]
    },
    {
      name: "AI 算力",
      change: "+3.76%",
      score: 89,
      leader: "工业富联",
      reason: "AI 服务器需求持续提升，资金关注度高。",
      trendCore: "中际旭创",
      reboundStock: "浪潮信息",
      risk: "短线涨幅较大，注意一致性过强后的分化。",
      relatedStocks: ["工业富联", "中际旭创", "浪潮信息", "新易盛"]
    },
    {
      name: "半导体",
      change: "+2.91%",
      score: 85,
      leader: "通富微电",
      reason: "国产替代与封测方向走强。",
      trendCore: "北方华创",
      reboundStock: "长电科技",
      risk: "轮动节奏快，不能只看单日涨幅。",
      relatedStocks: ["通富微电", "北方华创", "长电科技", "中芯国际"]
    }
  ],
  watchlist: [
    {
      code: "601138",
      name: "工业富联",
      score: 91,
      risk: "Medium",
      nextAction: "等待回踩 5 日线"
    },
    {
      code: "002415",
      name: "海康威视",
      score: 76,
      risk: "Low",
      nextAction: "继续观察"
    }
  ],
  riskAlerts: [
    "高位连板股分歧加大，注意炸板风险。",
    "AI 算力方向短线涨幅较大，避免盲目追高。",
    "市场成交额虽放大，但部分板块轮动较快。"
  ]
};
