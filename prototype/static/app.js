const $ = (selector) => document.querySelector(selector);

const state = {
  radar: null,
  workspace: null,
  view: "workspace",
  watchlist: [],
  selectedSector: "",
  hiddenQueue: [],
  completedQueue: [],
};

const fmt = (value, suffix = "") => {
  if (value === null || value === undefined || value === "" || Number.isNaN(value)) return "待确认";
  return `${value}${suffix}`;
};

const esc = (value) =>
  String(value ?? "待确认").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);

const trendClass = (value) => (value > 0 ? "up" : value < 0 ? "down" : "flat");

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function setStatus(text, loading = false) {
  $("#status").innerHTML = loading ? `<span class="loader"></span>${esc(text)}` : esc(text);
}

function parseStocks() {
  return $("#stockInput").value
    .replaceAll("，", ",")
    .replaceAll("\n", ",")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function metric(label, value, cls = "") {
  return `<div class="metric"><span>${esc(label)}</span><strong class="${cls}">${esc(value)}</strong></div>`;
}

function loadWatchlist() {
  try {
    state.watchlist = JSON.parse(localStorage.getItem("stockWatchlist") || "[]");
  } catch {
    state.watchlist = [];
  }
}

function saveWatchlist() {
  localStorage.setItem("stockWatchlist", JSON.stringify(state.watchlist));
}

function showView(view) {
  state.view = view;
  document.querySelectorAll(".side-nav").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  const analysisViews = new Set(["stocks", "analysis"]);
  $("#workspaceView").hidden = analysisViews.has(view);
  $("#analysisView").hidden = !analysisViews.has(view);
  if (view === "market" || view === "sector" || view === "watchlist" || view === "reports" || view === "review" || view === "settings") {
    renderWorkspace(state.radar, view);
  }
}

function emotionClass(score) {
  if (score >= 80) return "good";
  if (score >= 60) return "watch";
  if (score >= 40) return "neutral";
  return "bad";
}

function renderWorkspace(data, mode = "workspace") {
  const market = data.market || {};
  const summary = data.summary || {};
  const stats = market.stats || {};
  const queue = buildResearchQueue(data).filter((item) => !state.hiddenQueue.includes(item.code));
  const risks = queue.filter((item) => (item.risk_score || 0) >= 70).slice(0, 4);
  $("#workspaceView").innerHTML = `
    <section class="workspace-header">
      <div>
        <span class="eyebrow">${esc(modeLabel(mode))}</span>
        <h1>Research Workspace</h1>
        <p>Research > Decision。AI 负责收集、整理、分析、总结和提醒；用户负责判断、决策和交易。</p>
      </div>
      <div class="workflow-steps" aria-label="研究流程">
        <span>市场</span>
        <span>板块</span>
        <span>队列</span>
        <span>风险</span>
        <span>下一步</span>
      </div>
    </section>

    <section class="panel market-pulse ${emotionClass(market.emotion_score || 0)}">
      <div>
        <span class="eyebrow">Market Pulse</span>
        <h2>${esc(fmt(market.emotion_score))} 分</h2>
        <p>${esc(market.emotion_label || "判断待确认")}</p>
        <strong>${esc(market.advice || "")}</strong>
        <div class="module-actions"><button class="ghost-button compact-button" type="button" data-refresh-module="marketPulse">Refresh</button></div>
      </div>
      <div class="pulse-grid">
        ${metric("两市成交额", `${fmt(stats.amount_yi)}亿`)}
        ${metric("上涨家数", fmt(stats.rising_count), "up")}
        ${metric("下跌家数", fmt(stats.falling_count), "down")}
        ${metric("涨停家数", fmt(stats.limit_up_count), "up")}
        ${metric("跌停家数", fmt(stats.limit_down_count), "down")}
        ${metric("炸板率估算", fmt(stats.failed_limit_rate, "%"))}
        ${metric("连板高度", "数据源待接入")}
        ${metric("热门方向", (summary.focus_directions || []).join("、") || "待确认")}
      </div>
    </section>

    <section class="panel ai-brief-card">
      <div class="section-title">
        <h3>AI Daily Brief</h3>
        <button class="ghost-button compact-button" type="button" data-refresh-module="dailyBrief">Refresh</button>
        <span>不超过 300 字</span>
      </div>
      <p>${esc(buildDailyBrief(data))}</p>
      <div class="brief-actions">
        <button class="ghost-button compact-button" type="button">展开全文</button>
        <button class="ghost-button compact-button" type="button">生成长报告</button>
        <button class="ghost-button compact-button" type="button">导出 Markdown</button>
      </div>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>Research Queue</h3>
        <button class="ghost-button compact-button" type="button" data-refresh-module="researchQueue">Refresh</button>
        <span>按风险最高、买点出现、热门板块、用户关注度排序</span>
      </div>
      <div class="queue-list">
        ${queue.map(queueCardV2).join("") || `<div class="empty">研究队列为空</div>`}
      </div>
    </section>

    <section class="workspace-two-col">
      <section class="panel">
        <div class="section-title">
          <h3>Hot Sectors</h3>
          <button class="ghost-button compact-button" type="button" data-refresh-module="hotSectors">Refresh</button>
          <span>Part 2 将补完整交互</span>
        </div>
        <div class="sector-strip">
          ${(data.sectors || []).slice(0, mode === "sector" ? 8 : 4).map(sectorCardV2).join("")}
        </div>
      </section>

      <section class="panel">
        <div class="section-title">
          <h3>Risk Alerts</h3>
          <span>风险提示优先于买点提示</span>
        </div>
        <div class="risk-alert-list">
          ${risks.map(riskAlert).join("") || `<div class="empty">当前队列未触发高风险提醒</div>`}
        </div>
      </section>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>Watchlist Changes</h3>
        <span>用户观察池变化</span>
      </div>
      <div class="watch-summary">
        ${metric("观察池股票", fmt(state.watchlist.length))}
        ${metric("待研究", fmt(state.watchlist.filter((item) => item.status === "等待买点").length))}
        ${metric("风险升高", fmt(state.watchlist.filter((item) => item.risk_signal === "风险升高").length), "down")}
        ${metric("下一步", nextActionText(data))}
      </div>
    </section>
  `;
  $("#copilotText").textContent = nextActionText(data);
  bindCandidateActions($("#workspaceView"));
  bindWorkspaceActions($("#workspaceView"));
  if (mode === "sector") {
    $("#workspaceView").insertAdjacentHTML("beforeend", sectorDetailSection(data));
    bindWorkspaceActions($("#workspaceView"));
  }
  if (mode === "watchlist") {
    $("#workspaceView").insertAdjacentHTML("beforeend", watchlistWorkspaceSection());
    bindWatchlistActions($("#workspaceView"));
  }
  renderCopilotTools(data);
}

function modeLabel(mode) {
  const labels = {
    workspace: "Workspace",
    market: "Market",
    sector: "Sector",
    watchlist: "Watchlist",
    reports: "Research Reports",
    review: "Review",
    settings: "Settings",
  };
  return labels[mode] || "Workspace";
}

function buildDailyBrief(data) {
  const market = data.market || {};
  const summary = data.summary || {};
  const sectors = (data.sectors || []).slice(0, 3).map((item) => item.name).join("、") || "热点待确认";
  const riskCount = summary.risk_count || 0;
  return `今日市场情绪为${fmt(market.emotion_score)}分，${market.emotion_label || "处于待确认状态"}。当前值得优先研究的方向包括${sectors}。研究队列中有${fmt(summary.focus_count)}只股票值得继续跟踪，${fmt(summary.buy_signal_count)}只出现买点线索，${fmt(riskCount)}只风险升高。今日建议：${summary.suggestion || "先看板块，再看个股，风险提示优先。"}`;
}

function buildResearchQueue(data) {
  return (data.candidates || [])
    .slice()
    .sort((a, b) => {
      const riskDiff = (b.risk_score || 0) - (a.risk_score || 0);
      if (riskDiff) return riskDiff;
      const buyDiff = (b.buy_point_score || 0) - (a.buy_point_score || 0);
      if (buyDiff) return buyDiff;
      return (b.overall_score || 0) - (a.overall_score || 0);
    })
    .slice(0, 8);
}

function queueCard(item) {
  const status = (item.risk_score || 0) >= 70 ? "待研究" : (item.buy_point_score || 0) >= 65 ? "跟踪中" : "待研究";
  const nextStep = (item.risk_score || 0) >= 70 ? "先确认风险是否释放" : (item.buy_point_score || 0) >= 65 ? "观察买点是否继续成立" : "等待板块和资金确认";
  return `
    <article class="queue-card">
      <div>
        <strong>${esc(item.name)}</strong>
        <small>${esc(item.code)} · ${esc(item.industry || "行业待确认")}</small>
      </div>
      <span>综合 ${esc(fmt(item.overall_score))}</span>
      <span>${esc(status)}</span>
      <small>${esc(item.updated_at || "最近分析：当前会话")}</small>
      <p>${esc(nextStep)}</p>
      <div class="candidate-actions">
        <button type="button" data-analyze="${esc(item.code)}">研究</button>
        <button class="ghost-button" type="button" data-watch="${esc(item.code)}">加入观察池</button>
      </div>
    </article>
  `;
}

function queueCardV2(item) {
  const done = state.completedQueue.includes(item.code);
  const highRisk = (item.risk_score || 0) >= 70;
  const activeBuy = (item.buy_point_score || 0) >= 65 && !highRisk;
  const status = done ? "completed" : highRisk ? "risk-first" : activeBuy ? "tracking" : "pending";
  const nextStep = highRisk ? "先确认风险是否释放" : activeBuy ? "观察买点是否持续成立" : "等待板块和资金确认";
  return `
    <article class="queue-card ${done ? "completed" : ""}">
      <div>
        <strong>${esc(item.name)}</strong>
        <small>${esc(item.code)} · ${esc(item.industry || "industry pending")}</small>
      </div>
      <span>Score ${esc(fmt(item.overall_score))}</span>
      <span>${esc(status)}</span>
      <small>Risk ${esc(fmt(item.risk_score))} · Buy ${esc(fmt(item.buy_point_score))}</small>
      <p>${esc(nextStep)}</p>
      <div class="candidate-actions">
        <button type="button" data-analyze="${esc(item.code)}">研究</button>
        <button class="ghost-button" type="button" data-watch="${esc(item.code)}">加入 Watchlist</button>
        <button class="ghost-button" type="button" data-queue-done="${esc(item.code)}">${done ? "已完成" : "标记完成"}</button>
        <button class="ghost-button danger-button" type="button" data-queue-remove="${esc(item.code)}">移除任务</button>
      </div>
    </article>
  `;
}

function riskAlert(item) {
  return `
    <article class="risk-alert">
      <strong>${esc(item.name)} ${esc(item.code)}</strong>
      <p>风险分 ${esc(fmt(item.risk_score))}。${esc(item.candidate_reason)}</p>
    </article>
  `;
}

function nextActionText(data) {
  const sectors = (data.sectors || []).slice(0, 2).map((item) => item.name).join("、") || "热点板块";
  const riskCount = data.summary?.risk_count || 0;
  if (riskCount > 0) return `先处理风险升高股票，再研究${sectors}里的趋势中军。`;
  return `优先研究${sectors}，把候选股加入观察池，等待买点。`;
}

function indexCard(item) {
  const quote = item.quote || {};
  return `
    <article class="index-card">
      <strong>${esc(item.target?.name || quote.name || "指数")}</strong>
      <span class="${trendClass(quote.change_pct)}">${esc(fmt(quote.change_pct, "%"))}</span>
      <small>${esc(item.state || "")}</small>
    </article>
  `;
}

function sectorCard(item) {
  return `
    <article class="sector-card">
      <div>
        <strong>${esc(item.name)}</strong>
        <span class="${trendClass(item.change_pct)}">${esc(fmt(item.change_pct, "%"))}</span>
      </div>
      <div class="heat-meter"><i style="width:${Math.max(0, Math.min(100, item.heat_score || 0))}%"></i></div>
      <small>热度 ${esc(fmt(item.heat_score))} · 成交 ${esc(fmt(item.amount_yi))}亿</small>
      <small>主力 ${esc(fmt(item.main_net_inflow_yi))}亿 · 涨停 ${esc(fmt(item.limit_up_count))}</small>
      <small>龙头：${esc(item.leader)}</small>
    </article>
  `;
}

function sectorCardV2(item) {
  const name = item.name || "";
  return `
    <article class="sector-card sector-card-action" data-sector-card="${esc(name)}">
      <div>
        <strong>${esc(name)}</strong>
        <span class="${trendClass(item.change_pct)}">${esc(fmt(item.change_pct, "%"))}</span>
      </div>
      <div class="heat-meter"><i style="width:${Math.max(0, Math.min(100, item.heat_score || 0))}%"></i></div>
      <small>Heat ${esc(fmt(item.heat_score))} · Amount ${esc(fmt(item.amount_yi))} yi</small>
      <small>Flow ${esc(fmt(item.main_net_inflow_yi))} yi · Limit up ${esc(fmt(item.limit_up_count))}</small>
      <small>Leader: ${esc(item.leader || "")} · Core: ${esc(item.trend_core || item.leader || "")}</small>
      <p>${esc(item.ai_summary || item.conclusion || item.catalyst || "")}</p>
      <button class="ghost-button compact-button" type="button" data-sector="${esc(name)}">Open sector</button>
    </article>
  `;
}

function bindWorkspaceActions(root) {
  root.querySelectorAll("[data-refresh-module]").forEach((button) => {
    button.addEventListener("click", () => refreshWorkspaceModule(button.dataset.refreshModule));
  });
  root.querySelectorAll("[data-queue-done]").forEach((button) => {
    button.addEventListener("click", async () => {
      const code = button.dataset.queueDone;
      if (!state.completedQueue.includes(code)) state.completedQueue.push(code);
      await sendTelemetry("research_queue_completed", "researchQueue", { code });
      renderWorkspace(state.radar, state.view);
    });
  });
  root.querySelectorAll("[data-queue-remove]").forEach((button) => {
    button.addEventListener("click", async () => {
      const code = button.dataset.queueRemove;
      if (!state.hiddenQueue.includes(code)) state.hiddenQueue.push(code);
      await sendTelemetry("research_queue_removed", "researchQueue", { code });
      renderWorkspace(state.radar, state.view);
    });
  });
  root.querySelectorAll("[data-sector]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedSector = button.dataset.sector;
      sendTelemetry("sector_click", "hotSectors", { sector: state.selectedSector });
      showView("sector");
    });
  });
  root.querySelectorAll("[data-sector-card]").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("button")) return;
      state.selectedSector = card.dataset.sectorCard;
      sendTelemetry("sector_click", "hotSectors", { sector: state.selectedSector });
      showView("sector");
    });
  });
  root.querySelectorAll("[data-go-queue]").forEach((button) => {
    button.addEventListener("click", () => showView("workspace"));
  });
}

function sectorDetailSection(data) {
  const sectors = data.sectors || [];
  const sector = sectors.find((item) => item.name === state.selectedSector) || sectors[0] || {};
  state.selectedSector = sector.name || state.selectedSector;
  const members = (sector.members && sector.members.length ? sector.members : data.candidates || []).slice(0, 8);
  return `
    <section class="panel sector-detail">
      <div class="section-title">
        <h3>${esc(sector.name || "Sector Detail")}</h3>
        <span>Members · Leaders · AI report · Heat history · Fund flow · News</span>
      </div>
      <div class="sector-detail-grid">
        <article>
          <span class="eyebrow">AI sector report</span>
          <p>${esc(sector.ai_summary || sector.conclusion || sector.catalyst || "No sector summary yet.")}</p>
          <div class="watch-tags">
            <span>Leader ${esc(sector.leader || "Pending")}</span>
            <span>Core ${esc(sector.trend_core || sector.leader || "Pending")}</span>
            <span>Fund ${esc(fmt(sector.fund_flow ?? sector.main_net_inflow_yi))} yi</span>
          </div>
        </article>
        <article>
          <span class="eyebrow">Leader ranking</span>
          <div class="mini-rank-list">
            ${members.map((item, index) => `<button class="ghost-button mini-rank" type="button" data-analyze="${esc(item.code)}"><b>${index + 1}</b><span>${esc(item.name)}</span><small>${esc(item.code)} · ${esc(fmt(item.overall_score))}</small></button>`).join("") || `<div class="empty">No members yet.</div>`}
          </div>
        </article>
      </div>
      <div class="sector-news-row">
        ${(sector.news || []).map((item) => `<span>${esc(item)}</span>`).join("") || `<span>Sector news source pending.</span>`}
      </div>
    </section>
  `;
}

function riskLevel(item) {
  const score = item.risk_score ?? item.risk ?? 0;
  if (score >= 70 || item.risk_signal === "风险升高") return "High";
  if (score >= 45) return "Medium";
  return "Low";
}

function nextWatchAction(item) {
  if ((item.risk_score || 0) >= 70 || item.risk_signal === "风险升高") return "放弃研究";
  if ((item.buy_point_score || 0) >= 65 || item.buy_signal === "买点观察") return "买入";
  return "等待";
}

function watchlistWorkspaceSection() {
  if (!state.watchlist.length) {
    return `
      <section class="panel empty-state-panel">
        <h3>开始研究第一只股票</h3>
        <p>Watchlist is for possible future trades, not simple favorites.</p>
        <button type="button" data-go-queue>前往 Research Queue</button>
      </section>
    `;
  }
  const rows = state.watchlist.slice().sort((a, b) => Number(Boolean(b.pinned)) - Number(Boolean(a.pinned)));
  return `
    <section class="panel">
      <div class="section-title">
        <h3>Watchlist</h3>
        <span>Future possible trades · supports delete, pin, alert and completion</span>
      </div>
      <div class="watch-list workspace-watch-list">
        ${rows.map(watchCardV2).join("")}
      </div>
    </section>
  `;
}

function watchCardV2(item) {
  const level = item.risk_level || riskLevel(item);
  return `
    <article class="watch-card watch-card-v2 ${item.pinned ? "pinned" : ""}">
      <div>
        <strong>${esc(item.name)} <small>${esc(item.code)}</small></strong>
        <p>${esc(item.change_summary || item.reason || "Waiting for the next research update.")}</p>
        <div class="watch-tags">
          <span>Score ${esc(fmt(item.score))}</span>
          <span class="${level === "High" ? "down" : level === "Low" ? "up" : ""}">Risk ${esc(level)}</span>
          <span>Next ${esc(item.next_action || nextWatchAction(item))}</span>
          ${item.alert ? "<span>Alert on</span>" : ""}
          ${item.done ? "<span>Done</span>" : ""}
        </div>
      </div>
      <div class="candidate-actions">
        <button type="button" data-watch-analyze="${esc(item.code)}">查看报告</button>
        <button class="ghost-button" type="button" data-pin-watch="${esc(item.code)}">${item.pinned ? "取消 Pin" : "Pin 到顶部"}</button>
        <button class="ghost-button" type="button" data-alert-watch="${esc(item.code)}">${item.alert ? "取消提醒" : "设置提醒"}</button>
        <button class="ghost-button" type="button" data-done-watch="${esc(item.code)}">标记完成</button>
        <button class="ghost-button danger-button" type="button" data-remove-watch="${esc(item.code)}">删除</button>
      </div>
    </article>
  `;
}

function bindWatchlistActions(root) {
  root.querySelectorAll("[data-remove-watch]").forEach((button) => {
    button.addEventListener("click", () => {
      state.watchlist = state.watchlist.filter((item) => item.code !== button.dataset.removeWatch);
      saveWatchlist();
      sendTelemetry("watchlist_delete", "watchlist", { code: button.dataset.removeWatch });
      showView("watchlist");
    });
  });
  root.querySelectorAll("[data-pin-watch]").forEach((button) => {
    button.addEventListener("click", () => updateWatchItem(button.dataset.pinWatch, (item) => ({ ...item, pinned: !item.pinned })));
  });
  root.querySelectorAll("[data-alert-watch]").forEach((button) => {
    button.addEventListener("click", () => updateWatchItem(button.dataset.alertWatch, (item) => ({ ...item, alert: !item.alert })));
  });
  root.querySelectorAll("[data-done-watch]").forEach((button) => {
    button.addEventListener("click", () => updateWatchItem(button.dataset.doneWatch, (item) => ({ ...item, done: true, status: "已完成" })));
  });
  root.querySelectorAll("[data-watch-analyze]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#stockInput").value = button.dataset.watchAnalyze;
      showView("analysis");
      analyzeFirst();
    });
  });
  bindCandidateActions(root);
}

function updateWatchItem(code, updater) {
  state.watchlist = state.watchlist.map((item) => (item.code === code ? updater(item) : item));
  saveWatchlist();
  sendTelemetry("watchlist_add", "watchlist", { code: item.code });
  showView("watchlist");
}

function renderCopilotTools(data) {
  const body = $("#aiCopilot .copilot-body");
  if (!body || body.dataset.ready === "true") return;
  body.dataset.ready = "true";
  body.insertAdjacentHTML("beforeend", `
    <div class="copilot-tools">
      <button class="ghost-button compact-button" type="button" data-copilot-intent="market">总结市场</button>
      <button class="ghost-button compact-button" type="button" data-copilot-intent="compare">对比股票</button>
      <button class="ghost-button compact-button" type="button" data-copilot-intent="sector">分析板块</button>
      <button class="ghost-button compact-button" type="button" data-copilot-intent="score">解释评分</button>
      <button class="ghost-button compact-button" type="button" data-copilot-intent="next">下一步任务</button>
    </div>
    <div id="copilotStructured" class="copilot-structured"></div>
  `);
  body.querySelectorAll("[data-copilot-intent]").forEach((button) => {
    button.addEventListener("click", () => renderCopilotAnswer(button.dataset.copilotIntent));
  });
  renderCopilotAnswer("next");
}

function renderCopilotAnswer(intent) {
  const target = $("#copilotStructured");
  if (!target) return;
  const data = state.radar || {};
  const sector = (data.sectors || [])[0] || {};
  const risk = (data.candidates || []).find((item) => (item.risk_score || 0) >= 70) || {};
  const answers = {
    market: ["原因", buildDailyBrief(data), "龙头", sector.leader || "Pending", "中军", sector.trend_core || sector.leader || "Pending", "风险", "风险分越高越危险，先看风险再看机会。", "后续观察点", "热点能否持续、成交额是否放大、风险股是否减少。"],
    compare: ["原因", "先比较综合分、风险分、买点分，不把综合分当买卖信号。", "龙头", sector.leader || "Pending", "中军", sector.trend_core || sector.leader || "Pending", "风险", "高风险股只做解释，不直接进入交易判断。", "后续观察点", "把候选股加入 Watchlist 后继续跟踪变化。"],
    sector: ["原因", sector.ai_summary || sector.conclusion || "板块热度需要继续确认。", "龙头", sector.leader || "Pending", "中军", sector.trend_core || sector.leader || "Pending", "风险", "如果板块热度下降，不追后排。", "后续观察点", "看龙头强度、趋势中军承接和资金流向。"],
    score: ["原因", "评分用于排序研究优先级，不是交易指令。", "龙头", sector.leader || "Pending", "中军", sector.trend_core || sector.leader || "Pending", "风险", `${risk.name || "High risk names"} risk score ${fmt(risk.risk_score)}; higher means more dangerous.`, "后续观察点", "风险分升高时先降优先级。"],
    next: ["原因", nextActionText(data), "龙头", sector.leader || "Pending", "中军", sector.trend_core || sector.leader || "Pending", "风险", "风险提示优先级高于买点提示。", "后续观察点", "先看 Hot Sectors，再处理 Research Queue，最后更新 Watchlist。"],
  };
  const rows = answers[intent] || answers.next;
  target.innerHTML = `<dl>${rows.map((item, index) => index % 2 === 0 ? `<dt>${esc(item)}</dt>` : `<dd>${esc(item)}</dd>`).join("")}</dl>`;
}

function renderSectors(data) {
  $("#sectorsView").innerHTML = `
    <section class="panel">
      <div class="section-title">
        <h3>板块排行</h3>
        <span>先找板块，再找股票</span>
      </div>
      <div class="sector-table">
        ${(data.sectors || []).map((item, index) => `
          <article class="sector-row">
            <span class="rank-no">${index + 1}</span>
            <strong>${esc(item.name)}</strong>
            <span class="${trendClass(item.change_pct)}">${esc(fmt(item.change_pct, "%"))}</span>
            <span>${esc(fmt(item.heat_score))} 分</span>
            <span>${esc(fmt(item.amount_yi))}亿</span>
            <span>${esc(fmt(item.main_net_inflow_yi))}亿</span>
            <small>${esc(item.leader)} · ${esc(item.catalyst)}</small>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderScreener(data) {
  $("#screenerView").innerHTML = `
    <section class="panel">
      <div class="section-title">
        <h3>股票筛选器</h3>
        <span>默认过滤风险过高和综合分过低股票</span>
      </div>
      <div class="filter-bar">
        <select id="gradeFilter">
          <option value="">全部等级</option>
          <option value="重点关注">重点关注</option>
          <option value="加入观察池">加入观察池</option>
          <option value="一般关注">一般关注</option>
        </select>
        <select id="shapeFilter">
          <option value="">全部形态</option>
          <option value="强趋势">强趋势</option>
          <option value="趋势偏强">趋势偏强</option>
          <option value="平台整理">平台整理</option>
          <option value="破位下跌">破位下跌</option>
        </select>
        <label class="check-row"><input id="hideFiltered" type="checkbox" checked /> 隐藏暂不关注</label>
      </div>
      <div id="candidateList" class="candidate-list"></div>
    </section>
  `;
  $("#gradeFilter").addEventListener("change", refreshCandidateList);
  $("#shapeFilter").addEventListener("change", refreshCandidateList);
  $("#hideFiltered").addEventListener("change", refreshCandidateList);
  refreshCandidateList();
}

function refreshCandidateList() {
  const grade = $("#gradeFilter")?.value || "";
  const shape = $("#shapeFilter")?.value || "";
  const hide = $("#hideFiltered")?.checked;
  let rows = state.radar?.candidates || [];
  if (grade) rows = rows.filter((item) => item.grade === grade);
  if (shape) rows = rows.filter((item) => item.technical_shape === shape);
  if (hide) rows = rows.filter((item) => !item.filtered_out);
  $("#candidateList").innerHTML = rows.map(candidateCard).join("") || `<div class="empty">没有符合条件的股票</div>`;
  bindCandidateActions($("#candidateList"));
}

function candidateCard(item) {
  return `
    <article class="candidate-card ${item.filtered_out ? "muted-card" : ""}">
      <div class="candidate-main">
        <div>
          <strong>${esc(item.name)}</strong>
          <small>${esc(item.code)} · ${esc(item.technical_shape)} · ${esc(item.grade)}</small>
        </div>
        <p>${esc(item.candidate_reason)}</p>
      </div>
      <div class="candidate-scores">
        <span>综合 <b>${esc(fmt(item.overall_score))}</b></span>
        <span>买点 <b>${esc(fmt(item.buy_point_score))}</b></span>
        <span>风险 <b class="${(item.risk_score || 0) >= 70 ? "down" : ""}">${esc(fmt(item.risk_score))}</b></span>
      </div>
      <div class="candidate-actions">
        <button type="button" data-analyze="${esc(item.code)}">分析</button>
        <button class="ghost-button" type="button" data-watch="${esc(item.code)}">加入观察池</button>
      </div>
    </article>
  `;
}

function bindCandidateActions(root) {
  root.querySelectorAll("[data-analyze]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#stockInput").value = button.dataset.analyze;
      showView("analysis");
      analyzeFirst();
    });
  });
  root.querySelectorAll("[data-watch]").forEach((button) => {
    button.addEventListener("click", () => addToWatchlist(button.dataset.watch));
  });
}

function addToWatchlist(code) {
  const item = (state.radar?.candidates || []).find((row) => row.code === code);
  if (!item) return;
  if (state.watchlist.some((row) => row.code === code)) {
    setStatus(`${item.name} 已在观察池中。`);
    return;
  }
  state.watchlist.unshift({
    code: item.code,
    name: item.name,
    reason: item.watch_reason,
    score: item.overall_score,
    status: "等待买点",
    risk_signal: item.risk_signal,
    risk_score: item.risk_score,
    risk_level: riskLevel(item),
    buy_signal: item.buy_signal,
    next_action: nextWatchAction(item),
    change_summary: item.candidate_reason || item.watch_reason,
    source: "Research Queue",
    added_at: new Date().toLocaleDateString("zh-CN"),
  });
  saveWatchlist();
  setStatus(`${item.name} 已加入观察池。`);
}

function renderWatchlist() {
  $("#watchlistView").innerHTML = `
    <section class="panel">
      <div class="section-title">
        <h3>观察池</h3>
        <span>先跟踪，再等买点</span>
      </div>
      <div class="watch-list">
        ${state.watchlist.map(watchCard).join("") || `<div class="empty">观察池为空。可在市场雷达或股票筛选器里加入股票。</div>`}
      </div>
    </section>
  `;
  $("#watchlistView").querySelectorAll("[data-remove-watch]").forEach((button) => {
    button.addEventListener("click", () => {
      state.watchlist = state.watchlist.filter((item) => item.code !== button.dataset.removeWatch);
      saveWatchlist();
      renderWatchlist();
    });
  });
  $("#watchlistView").querySelectorAll("[data-watch-analyze]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#stockInput").value = button.dataset.watchAnalyze;
      showView("analysis");
      analyzeFirst();
    });
  });
}

function watchCard(item) {
  return `
    <article class="watch-card">
      <div>
        <strong>${esc(item.name)}</strong>
        <small>${esc(item.code)} · ${esc(item.added_at)} · ${esc(item.status)}</small>
        <p>${esc(item.reason)}</p>
        <div class="watch-tags">
          <span>评分 ${esc(fmt(item.score))}</span>
          <span>${esc(item.buy_signal)}</span>
          <span class="${item.risk_signal === "风险升高" ? "down" : ""}">${esc(item.risk_signal)}</span>
        </div>
      </div>
      <div class="candidate-actions">
        <button type="button" data-watch-analyze="${esc(item.code)}">分析</button>
        <button class="ghost-button danger-button" type="button" data-remove-watch="${esc(item.code)}">移出</button>
      </div>
    </article>
  `;
}

function contextLine(label, text) {
  return `<p><strong>${esc(label)}：</strong>${esc(text || "待确认")}</p>`;
}

function levelCards(items, type) {
  if (!items?.length) return `<div class="empty">数据待行情接口确认</div>`;
  return items.map((item) => `
    <article class="level-tag ${type}">
      <span>${esc(item.label)}</span>
      <strong>${esc(fmt(item.price))}</strong>
      <small>${esc(item.reason || "行情接口未给出原因")}</small>
    </article>
  `).join("");
}

function actionCard(title, text) {
  return `<article class="action-card"><strong>${esc(title)}</strong><p>${esc(text || "待确认")}</p></article>`;
}

function maRows(items) {
  if (!items?.length) return `<div class="empty">均线数据待行情接口确认</div>`;
  return items.slice(0, 6).map((item) => {
    const cls = item.distance_pct > 0.5 ? "up" : item.distance_pct < -0.5 ? "down" : "flat";
    return `
      <div class="ma-row">
        <div class="ma-title"><strong>${esc(item.name)}</strong><span class="${cls}">${esc(item.status)}</span></div>
        <div class="ma-price">${esc(fmt(item.price))}</div>
        <div class="ma-meta"><span class="${cls}">${esc(fmt(item.distance_pct, "%"))}</span><small>${esc(item.tip || "")}</small></div>
      </div>
    `;
  }).join("");
}

function signalLabel(direction) {
  if (direction === "bullish") return "偏利好";
  if (direction === "bearish") return "偏风险";
  return "中性";
}

function signalCards(signals) {
  if (!signals?.length) return `<div class="empty">未触发明显信号</div>`;
  return signals.slice(0, 8).map((item) => `
    <article class="signal-card ${item.direction}">
      <div><strong>${esc(item.title)}</strong><span>${esc(signalLabel(item.direction))} · 强度 ${esc(item.strength)}/5</span></div>
      <p>${esc(item.detail)}</p>
    </article>
  `).join("");
}

function scoreExplain(label, value) {
  if (value === null || value === undefined) return "评分待数据源确认";
  if (label === "风险") return value >= 70 ? "风险分越高越危险，当前优先防回撤" : value >= 45 ? "风险中等，重点看支撑和均线" : "风险分较低，但不代表没有风险";
  if (label === "综合") return "综合分只是参考，不是买卖信号";
  if (value >= 70) return "该项相对占优";
  if (value >= 45) return "中性，需要结合位置观察";
  return "该项偏弱";
}

function scorePill(label, value) {
  const cls = label === "风险"
    ? value >= 70 ? "bad" : value >= 45 ? "watch" : "good"
    : value >= 70 ? "good" : value >= 45 ? "watch" : "bad";
  return `<div class="score-pill ${cls}"><span>${esc(label)}</span><strong>${esc(value ?? "待确认")}</strong><small>${esc(scoreExplain(label, value))}</small></div>`;
}

function renderSingle(data) {
  if (!data.ok) {
    $("#singleResult").innerHTML = `<section class="panel error">${esc(data.error || "分析失败")}</section>`;
    return;
  }
  const q = data.quote || {};
  const j = data.judgement || {};
  const s = data.scores || {};
  const p = data.position || {};
  const ma = data.moving_averages || {};
  const summary = data.signal_summary || {};

  $("#compareResult").innerHTML = "";
  $("#singleResult").innerHTML = `
    <section class="panel stock-head">
      <div>
        <span class="eyebrow">${esc(data.code)} · ${esc(data.market || "A股")}</span>
        <h2>${esc(data.name)}</h2>
        <div class="hero-tags"><span class="status-label">${esc(j.status || "待确认")}</span><span>风险：${esc(j.risk_level || "待确认")}</span><span>更新：${esc(fmt(q.update_time))}</span></div>
      </div>
      <div class="hero-price"><strong>${esc(fmt(q.price))}</strong><span class="${trendClass(q.change_pct)}">${esc(fmt(q.change_pct, "%"))}</span></div>
    </section>
    <section class="panel conclusion-panel"><span>AI 总结</span><h3>${esc(j.summary || "结论待行情接口确认")}</h3></section>
    <section class="panel quick-context">${contextLine("主营业务", data.context?.business)}${contextLine("近期公告", data.context?.latest_notice)}${contextLine("上涨/下跌逻辑", data.context?.move_reason)}</section>
    <section class="panel"><div class="section-title"><h3>关键支撑 / 压力</h3><span>每个价位都保留原因</span></div><div class="level-grid"><div><h4>支撑</h4>${levelCards(data.levels?.supports, "support")}</div><div><h4>压力</h4>${levelCards(data.levels?.resistances, "resistance")}</div></div></section>
    <section class="panel"><h3>短线 / 中线 / 长期判断</h3><div class="text-report"><p><strong>短线：</strong>${esc(j.short_term || "待确认")}</p><p><strong>中线：</strong>${esc(j.mid_term || "待确认")}</p><p><strong>长期：</strong>${esc(j.long_term || "待确认")}</p></div></section>
    <section class="panel"><h3>操作参考</h3><div class="action-grid">${actionCard("没买", j.action_no_position)}${actionCard("有仓", j.action_has_position)}${actionCard("想补仓", j.action_add_position)}</div><p class="direct-conclusion">${esc(j.final_conclusion || "")}</p></section>
    <section class="panel"><div class="section-title"><h3>行情概览</h3><span>${esc(q.source || "")}</span></div><div class="metric-grid">${metric("现价", fmt(q.price))}${metric("涨跌幅", fmt(q.change_pct, "%"), trendClass(q.change_pct))}${metric("最高", fmt(q.high))}${metric("最低", fmt(q.low))}${metric("成交额", q.amount_yi ? `${q.amount_yi}亿` : fmt(q.amount))}${metric("换手率", fmt(q.turnover_rate, "%"))}${metric("阶段高点", fmt(p.stage_high))}${metric("高点回撤", fmt(p.drawdown_from_stage_high_pct, "%"), "down")}</div></section>
    <section class="panel"><div class="section-title"><h3>均线状态</h3><span>${esc(ma.summary || "")}</span></div><div class="ma-list">${maRows(ma.items)}</div></section>
    <section class="panel"><div class="section-title"><h3>信号依据</h3><span>${esc(summary.bias || "待确认")} · 多空 ${esc(fmt(summary.bullish))} / ${esc(fmt(summary.bearish))}</span></div><div class="signal-grid">${signalCards(data.signals)}</div></section>
    <section class="panel"><div class="section-title"><h3>参考评分</h3><span>风险分越高越危险，综合分不是买卖信号</span></div><div class="score-grid">${scorePill("综合", s.overall_score)}${scorePill("趋势", s.trend_score)}${scorePill("买点", s.buy_point_score)}${scorePill("风险", s.risk_score)}${scorePill("弹性", s.volatility_score)}${scorePill("基本面", s.fundamental_score)}</div></section>
  `;
}

function compareCard(item, index) {
  return `<article class="compare-card"><div><span class="rank-no">${index + 1}</span><strong>${esc(item.name)}</strong><small>${esc(item.code)} · ${esc(item.status)}</small><p>${esc(item.summary)}</p></div><div class="compare-score"><strong>${esc(fmt(item.overall_score))}</strong><span class="${trendClass(item.change_pct)}">${esc(fmt(item.change_pct, "%"))}</span><small>风险 ${esc(fmt(item.risk_score))}，越高越危险</small></div></article>`;
}

function renderCompare(data) {
  $("#singleResult").innerHTML = "";
  $("#compareResult").innerHTML = `<section class="panel compare-page-head"><div><span class="eyebrow">Compare</span><h2>多股对比</h2><p>${esc(data.conclusion || "按综合分和风险分做横向参考。")}</p></div></section><section class="compare-list">${(data.items || []).map(compareCard).join("") || `<div class="panel empty">没有可对比的数据</div>`}</section>`;
}

async function analyzeFirst() {
  const stocks = parseStocks();
  if (!stocks.length) {
    setStatus("请输入股票名称或代码。");
    return;
  }
  setStatus("正在读取行情、公告和均线数据...", true);
  try {
    const data = await getJson(`/api/analyze/stock?code=${encodeURIComponent(stocks[0])}`);
    renderSingle(data);
    setStatus(data.ok ? "分析完成。先看 AI 总结，再看关键价位和操作参考。" : data.error || "分析失败");
  } catch (error) {
    setStatus(`分析失败：${error.message}`);
  }
}

async function compareAll() {
  const stocks = parseStocks();
  if (stocks.length < 2) {
    setStatus("多股对比至少输入 2 只股票，用逗号或换行分隔。");
    return;
  }
  setStatus("正在对比多只股票...", true);
  try {
    const data = await postJson("/api/analyze/compare", { stocks: stocks.slice(0, 10) });
    renderCompare(data);
    setStatus("对比完成。风险分越高越危险，综合分只做参考。");
  } catch (error) {
    setStatus(`对比失败：${error.message}`);
  }
}

function workspaceSkeleton() {
  return `
    <section class="panel skeleton-panel">
      <div class="skeleton-line wide"></div>
      <div class="skeleton-grid">
        <span></span><span></span><span></span><span></span>
      </div>
    </section>
    <section class="panel skeleton-panel">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-line wide"></div>
    </section>
  `;
}

function workspaceError(error) {
  const id = `WS-${Date.now().toString(36).toUpperCase()}`;
  return `
    <section class="panel error-state-panel">
      <span class="eyebrow">Workspace Error</span>
      <h3>加载失败</h3>
      <p>${esc(error?.message || "Unknown error")}</p>
      <small>Error ID: ${esc(id)}</small>
      <div class="candidate-actions">
        <button id="retryWorkspace" type="button">Retry</button>
        <button class="ghost-button" type="button">查看详情</button>
      </div>
    </section>
  `;
}

async function refreshWorkspaceModule(module) {
  setStatus(`Refreshing ${module}...`, true);
  try {
    const data = await getJson(`/api/v1/workspace?module=${encodeURIComponent(module)}`);
    if (module === "hotSectors" && data.hotSectors) state.radar.sectors = data.hotSectors;
    if (module === "researchQueue" && data.researchQueue) state.radar.candidates = data.researchQueue;
    if (module === "marketPulse" && data.marketPulse) state.radar.market = data.marketPulse;
    await sendTelemetry("module_refresh", module, { state: data.state });
    renderWorkspace(state.radar, state.view);
    setStatus(`${module} refreshed.`);
  } catch (error) {
    setStatus(`${module} refresh failed: ${error.message}`);
  }
}

async function sendTelemetry(event, module, extra = {}) {
  try {
    await postJson("/api/v1/telemetry", { event, module, ...extra });
  } catch {
    // Telemetry must never block the research workflow.
  }
}

async function loadRadar() {
  $("#workspaceView").innerHTML = workspaceSkeleton();
  setStatus("正在加载市场情绪、热门板块和候选股票...", true);
  try {
    state.workspace = await getJson("/api/v1/workspace");
    state.radar = state.workspace.raw || state.workspace;
    state.radar.sectors = state.workspace.hotSectors || state.radar.sectors || [];
    state.radar.summary = state.radar.summary || {};
    renderWorkspace(state.radar, state.view);
    setStatus("Research Workspace 已更新。先看市场，再看队列；风险提示优先。");
  } catch (error) {
    $("#workspaceView").innerHTML = workspaceError(error);
    $("#retryWorkspace")?.addEventListener("click", loadRadar);
    setStatus(`Research Workspace 加载失败：${error.message}`);
  }
}

function init() {
  loadWatchlist();
  document.querySelectorAll(".side-nav").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
  $("#globalAnalyzeButton").addEventListener("click", () => {
    $("#stockInput").value = $("#globalStockInput").value.trim();
    showView("stocks");
    analyzeFirst();
  });
  $("#globalStockInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      $("#stockInput").value = $("#globalStockInput").value.trim();
      showView("stocks");
      analyzeFirst();
    }
  });
  $("#toggleCopilot").addEventListener("click", () => $("#aiCopilot").classList.toggle("collapsed"));
  window.addEventListener("keydown", (event) => {
    if (event.target && ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;
    const keyMap = {
      "1": "workspace",
      "2": "market",
      "3": "sector",
      "4": "stocks",
      "5": "watchlist",
      "6": "reports",
      "7": "review",
      "8": "settings",
    };
    if (keyMap[event.key]) showView(keyMap[event.key]);
  });
  $("#analyzeButton").addEventListener("click", analyzeFirst);
  $("#compareButton").addEventListener("click", compareAll);
  loadRadar();
  sendTelemetry("workspace_open", "workspace");
}

init();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/static/sw.js").catch(() => {}));
}
