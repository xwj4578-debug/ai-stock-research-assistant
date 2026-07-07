export type MarketPulse = {
  score: number;
  status: string;
  turnover: string;
  upCount: number;
  downCount: number;
  limitUp: number;
  limitDown: number;
  brokenRate: string;
  leadingHeight: string;
  summary: string;
};

export type DailyBrief = {
  title: string;
  content: string;
};

export type ResearchQueueItem = {
  code: string;
  name: string;
  score: number;
  status: string;
  reason: string;
  sector?: string;
  conclusion?: string;
  riseLogic?: string;
  riskTip?: string;
  nextStep?: string;
};

export type HotSector = {
  name: string;
  change: string;
  score: number;
  leader: string;
  reason: string;
  trendCore?: string;
  reboundStock?: string;
  risk?: string;
  relatedStocks?: string[];
};

export type WatchlistItem = {
  code: string;
  name: string;
  score: number;
  risk: "Low" | "Medium" | "High";
  nextAction: string;
  pinned?: boolean;
};

export type WorkspaceData = {
  marketPulse: MarketPulse;
  dailyBrief: DailyBrief;
  researchQueue: ResearchQueueItem[];
  hotSectors: HotSector[];
  watchlist: WatchlistItem[];
  riskAlerts: string[];
};
