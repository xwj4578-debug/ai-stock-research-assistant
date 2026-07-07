const $ = (selector) => document.querySelector(selector);

const state = {
  radar: null,
  view: "radar",
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
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  ["radar", "sectors", "screener", "watchlist", "analysis"].forEach((name) => {
    $(`#${name}View`).hidden = name !== view;
  });
  if (view === "watchlist") renderWatchlist();
}

function emotionClass(score) {
  if (score >= 80) return "good";
  if (score >= 60) return "watch";
  if (score >= 40) return "neutral";
  return "bad";
}

function renderRadar(data) {
  const market = data.market || {};
  const summary = data.summary || {};
  const stats = market.stats || {};
  $("#radarView").innerHTML = `
    <section class="panel radar-hero ${emotionClass(market.emotion_score || 0)}">
      <div>
        <span class="eyebrow">今日市场情绪</span>
        <h2>${esc(fmt(market.emotion_score))} 分</h2>
        <p>${esc(market.emotion_label || "判断待确认")}</p>
        <strong>${esc(market.advice || "")}</strong>
      </div>
      <div class="radar-summary">
        ${metric("重点关注股票", fmt(summary.focus_count))}
        ${metric("触发买点股票", fmt(summary.buy_signal_count))}
        ${metric("风险升高股票", fmt(summary.risk_count), "down")}
        ${metric("热门方向", (summary.focus_directions || []).join("、") || "待确认")}
      </div>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>市场宽度</h3>
        <span>${esc(stats.source || "公开行情聚合")}</span>
      </div>
      <div class="metric-grid">
        ${metric("两市成交额", `${fmt(stats.amount_yi)}亿`)}
        ${metric("上涨家数", fmt(stats.rising_count), "up")}
        ${metric("下跌家数", fmt(stats.falling_count), "down")}
        ${metric("涨停家数", fmt(stats.limit_up_count), "up")}
        ${metric("跌停家数", fmt(stats.limit_down_count), "down")}
        ${metric("炸板率估算", fmt(stats.failed_limit_rate, "%"))}
      </div>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>市场指数</h3>
        <span>用均线、涨跌幅和成交额估算市场风险</span>
      </div>
      <div class="index-grid">
        ${(market.indices || []).map(indexCard).join("")}
      </div>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>今日推荐关注方向</h3>
        <span>${esc(summary.suggestion || "")}</span>
      </div>
      <div class="sector-strip">
        ${(data.sectors || []).slice(0, 5).map(sectorCard).join("")}
      </div>
    </section>

    <section class="panel">
      <div class="section-title">
        <h3>重点关注股票</h3>
        <span>先加入观察池，再等买点</span>
      </div>
      <div class="candidate-list">
        ${(data.candidates || []).filter((item) => !item.filtered_out).slice(0, 6).map(candidateCard).join("")}
      </div>
    </section>
  `;
  bindCandidateActions($("#radarView"));
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
    renderRadar(state.radar);
    renderSectors(state.radar);
    renderScreener(state.radar);
    renderWatchlist();
    setStatus("市场雷达已更新。先看板块，再看个股；风险提示优先。");
  } catch (error) {
    setStatus(`市场雷达加载失败：${error.message}`);
  }
}

function init() {
  loadWatchlist();
  document.querySelectorAll(".tab-button").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
  $("#analyzeButton").addEventListener("click", analyzeFirst);
  $("#compareButton").addEventListener("click", compareAll);
  loadRadar();
}

init();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/static/sw.js").catch(() => {}));
}
