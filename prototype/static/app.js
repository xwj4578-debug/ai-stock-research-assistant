const $ = (selector) => document.querySelector(selector);

const state = {
  radar: null,
  view: "workspace",
  watchlist: [],
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
  const queue = buildResearchQueue(data);
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
        <span>按风险最高、买点出现、热门板块、用户关注度排序</span>
      </div>
      <div class="queue-list">
        ${queue.map(queueCard).join("") || `<div class="empty">研究队列为空</div>`}
      </div>
    </section>

    <section class="workspace-two-col">
      <section class="panel">
        <div class="section-title">
          <h3>Hot Sectors</h3>
          <span>Part 2 将补完整交互</span>
        </div>
        <div class="sector-strip">
          ${(data.sectors || []).slice(0, 4).map(sectorCard).join("")}
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
    buy_signal: item.buy_signal,
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

async function loadRadar() {
  setStatus("正在加载市场情绪、热门板块和候选股票...", true);
  try {
    state.radar = await getJson("/api/radar");
    renderWorkspace(state.radar, state.view);
    setStatus("Research Workspace 已更新。先看市场，再看队列；风险提示优先。");
  } catch (error) {
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
}

init();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/static/sw.js").catch(() => {}));
}
