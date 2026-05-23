/* HillTrade News Analyser — polling + render engine */

const AGENT_LABELS = {
  classifier:    "Classifying event type & scope",
  analogues:     "Finding historical analogues",
  causal_chain:  "Mapping causal chain (macro → sectors → stocks)",
  us_analyst:    "Analysing US market (NYSE / NASDAQ)",
  india_analyst: "Analysing Indian market (NSE / BSE)",
  macro_overlay: "Applying macro regime overlay",
  synthesizer:   "Synthesising final verdict",
};

const CONV_LABELS = { High: "high", Medium: "medium", Low: "low" };
const DUR_COLOURS = {
  "TEMPORARY":          "bg-amber-50 text-amber-700 border-amber-200",
  "CYCLICAL":           "bg-blue-50 text-blue-700 border-blue-200",
  "STRUCTURAL":         "bg-purple-50 text-purple-700 border-purple-200",
  "FUNDAMENTAL SHIFT":  "bg-rose-50 text-rose-700 border-rose-200",
};

let lastEventId   = 0;
let pollTimer     = null;
let agentStatuses = {};   // key → "running" | "done" | "error"
let finalResult   = null;

function initNewsPage() {
  processEvents(window.NEWS_INITIAL_EVENTS);

  if (window.NEWS_INITIAL_STATUS === "completed" || window.NEWS_INITIAL_STATUS === "failed") return;
  pollTimer = setInterval(poll, 2000);
}

async function poll() {
  try {
    const r = await fetch(`/api/news/${window.NEWS_ANALYSIS_ID}/events?since=${lastEventId}`);
    if (!r.ok) return;
    const data = await r.json();
    processEvents(data.events);
    if (data.status === "completed" || data.status === "failed") {
      clearInterval(pollTimer);
    }
  } catch (_) {}
}

function processEvents(events) {
  events.forEach(ev => {
    if (ev.id > lastEventId) lastEventId = ev.id;
    const d = typeof ev.data === "string" ? JSON.parse(ev.data) : ev.data;

    if (ev.event_type === "agent_started") {
      agentStatuses[d.agent] = "running";
      renderAgentTable();
    } else if (ev.event_type === "agent_done") {
      agentStatuses[d.agent] = "done";
      renderAgentTable();
      handleAgentResult(d.agent, d.result);
    } else if (ev.event_type === "agent_error") {
      agentStatuses[d.agent] = "error";
      renderAgentTable();
    } else if (ev.event_type === "complete") {
      finalResult = d.result;
      onComplete(d.result);
    } else if (ev.event_type === "error") {
      onError(d.message);
    }
  });
}

function renderAgentTable() {
  const el = document.getElementById("agent-table");
  const rows = Object.entries(AGENT_LABELS).map(([key, label]) => {
    const st = agentStatuses[key];
    let icon, colour;
    if (st === "running") {
      icon   = `<span class="spinner"></span>`;
      colour = "text-indigo-600";
    } else if (st === "done") {
      icon   = `<svg class="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`;
      colour = "text-slate-700";
    } else if (st === "error") {
      icon   = `<svg class="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>`;
      colour = "text-red-600";
    } else {
      icon   = `<span class="w-4 h-4 rounded-full border-2 border-slate-200 inline-block"></span>`;
      colour = "text-slate-400";
    }
    return `<div class="flex items-center gap-3">
      <div class="w-4 flex items-center justify-center shrink-0">${icon}</div>
      <span class="text-sm ${colour}">${label}</span>
    </div>`;
  });
  el.innerHTML = rows.join("");
}

/* ── per-agent result rendering ─────────────────────────────────────────── */

function handleAgentResult(agent, result) {
  if (!result) return;
  // If result is a string (double-stringified JSON), parse it
  if (typeof result === "string") {
    try { result = JSON.parse(result); } catch (_) { return; }
  }
  if (agent === "classifier")    renderClassification(result);
  if (agent === "analogues")     renderAnalogues(result);
  if (agent === "causal_chain")  renderCausalChain(result);
  if (agent === "us_analyst")    renderStocks("us", result);
  if (agent === "india_analyst") renderStocks("india", result);
  if (agent === "macro_overlay") renderMacro(result);
  if (agent === "synthesizer")   renderSynthesis(result);
}

/* Classification */
function renderClassification(c) {
  if (!c || typeof c !== "object" || Array.isArray(c)) return;

  // Defensive accessors — LLMs sometimes use alternate key names
  const title   = c.event_title   || c.title        || c.event_name   || c.headline     || "News Analysis";
  const type    = c.event_type    || c.type         || c.category     || "";
  const scope   = c.scope         || c.region       || c.geographic_scope || "";
  const novelty = c.novelty       || c.novelty_type || c.news_novelty  || "";
  const speed   = c.speed         || c.impact_speed || c.timeframe     || "";
  const usRel   = c.us_relevance  || c.us_impact    || c.usa_relevance || "";
  const inRel   = c.india_relevance || c.india_impact || "";
  const inNote  = c.india_relevance_reason || c.india_reason || c.india_context || "";
  const summary = c.event_summary || c.summary      || c.description  || "";
  const pricedIn = c.already_priced_in || c.priced_in || false;
  const pricedNote = c.priced_in_note  || c.priced_in_explanation || "";

  const el  = document.getElementById("section-classification");
  const nov = pricedIn
    ? `<span class="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">⚠ Likely already priced in</span>` : "";

  const badges = [
    [type,    "bg-indigo-50 text-indigo-700"],
    [scope,   "bg-slate-100 text-slate-600"],
    [novelty, "bg-sky-50 text-sky-700"],
    [speed,   "bg-violet-50 text-violet-700"],
    [usRel   ? `US: ${usRel}`    : null, usRel === "High"   ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"],
    [inRel   ? `India: ${inRel}` : null, inRel === "High"   ? "bg-orange-50 text-orange-700"  : "bg-slate-100 text-slate-600"],
  ].filter(([v]) => v).map(([v, cls]) =>
    `<span class="text-xs font-medium px-2.5 py-1 rounded-full ${cls}">${v}</span>`
  ).join("");

  el.innerHTML = `
    <div class="flex items-start justify-between gap-4 mb-3">
      <div>
        <h2 class="font-bold text-slate-900 text-lg leading-tight">${title}</h2>
        ${summary ? `<p class="text-sm text-slate-500 mt-1">${summary}</p>` : ""}
      </div>
      ${nov}
    </div>
    ${badges ? `<div class="flex flex-wrap gap-2">${badges}</div>` : ""}
    ${inNote  ? `<p class="text-xs text-slate-500 mt-3 italic">India: ${inNote}</p>` : ""}
    ${pricedNote ? `<p class="text-xs text-amber-600 mt-2">⚠ ${pricedNote}</p>` : ""}
  `;

  document.getElementById("event-title").textContent = title;
  document.getElementById("results-panel").classList.remove("hidden");
}

/* Historical Analogues */
function renderAnalogues(analogues) {
  if (!analogues || !analogues.length) return;
  const el = document.getElementById("section-analogues");
  el.classList.remove("hidden");

  const cards = analogues.map(a => `
    <div class="border border-slate-200 rounded-lg p-4">
      <div class="flex items-center justify-between mb-2">
        <h4 class="font-semibold text-slate-800 text-sm">${a.name}</h4>
      </div>
      <p class="text-xs text-slate-600 mb-3">${a.similarity_explanation || ""}</p>
      <div class="grid grid-cols-3 gap-3 mb-3 text-xs">
        <div class="bg-slate-50 rounded p-2">
          <div class="font-semibold text-slate-500 mb-1">5 Days</div>
          <div class="text-slate-700">${a.market_reaction_5d?.us_indices || "—"}</div>
          <div class="text-orange-600 mt-1">${a.market_reaction_5d?.indian_indices || ""}</div>
        </div>
        <div class="bg-slate-50 rounded p-2">
          <div class="font-semibold text-slate-500 mb-1">30 Days</div>
          <div class="text-slate-700">${a.market_reaction_30d?.trend_summary || a.market_reaction_30d?.us_indices || "—"}</div>
        </div>
        <div class="bg-slate-50 rounded p-2">
          <div class="font-semibold text-slate-500 mb-1">6 Months</div>
          <div class="text-slate-700">${a.market_reaction_6m?.trend_summary || a.market_reaction_6m?.us_indices || "—"}</div>
        </div>
      </div>
      <div class="bg-amber-50 border border-amber-100 rounded p-2.5 text-xs mb-2">
        <span class="font-semibold text-amber-700">What market got wrong: </span>
        <span class="text-amber-800">${a.initial_mispricing || "—"}</span>
      </div>
      <div class="bg-emerald-50 border border-emerald-100 rounded p-2.5 text-xs mb-2">
        <span class="font-semibold text-emerald-700">Correct trade: </span>
        <span class="text-emerald-800">${a.correct_trade || "—"}</span>
      </div>
      ${a.india_specific_lesson ? `<div class="bg-orange-50 border border-orange-100 rounded p-2.5 text-xs">
        <span class="font-semibold text-orange-700">India lesson: </span>
        <span class="text-orange-800">${a.india_specific_lesson}</span>
      </div>` : ""}
      ${a.divergence_from_current ? `<p class="text-xs text-slate-400 mt-2 italic">Caveat: ${a.divergence_from_current}</p>` : ""}
    </div>
  `).join("");

  el.innerHTML = `
    <h3 class="font-bold text-slate-800 mb-4">Historical Analogues</h3>
    <div class="space-y-4">${cards}</div>
  `;
}

/* Causal Chain */
function renderCausalChain(chain) {
  if (!chain || !Object.keys(chain).length) return;
  const el = document.getElementById("section-causal");
  el.classList.remove("hidden");

  const macro = chain.level1_macro || {};
  const macroRows = Object.entries({
    "GDP": macro.gdp_impact,
    "Inflation": macro.inflation_impact,
    "Rates (Fed/RBI)": macro.rate_trajectory,
    "Currencies": macro.currency_impact,
    "Commodities": macro.commodity_impact,
    "Risk Appetite": macro.risk_appetite,
    "Trade Flows": macro.trade_flow_impact,
  }).filter(([,v]) => v).map(([k, v]) => `
    <div class="flex gap-3 text-xs py-2 border-b border-slate-100 last:border-0">
      <span class="font-semibold text-slate-500 w-32 shrink-0">${k}</span>
      <span class="text-slate-700">${v}</span>
    </div>
  `).join("");

  const sectorRow = (s) => {
    const impactCls = s.impact === "positive" ? "text-emerald-600" :
                      s.impact === "negative" ? "text-red-500" : "text-slate-500";
    const magCls    = s.magnitude === "high" ? "bg-red-100 text-red-700" :
                      s.magnitude === "medium" ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600";
    return `<div class="flex gap-3 text-xs py-2 border-b border-slate-100 last:border-0">
      <span class="font-semibold text-slate-700 w-36 shrink-0">${s.sector}</span>
      <span class="${impactCls} font-semibold w-16 shrink-0 capitalize">${s.impact}</span>
      <span class="text-xs px-1.5 py-0.5 rounded font-medium ${magCls} shrink-0 h-fit">${s.magnitude}</span>
      <span class="text-slate-600">${s.reasoning || ""}</span>
    </div>`;
  };

  const usSectors    = (chain.level2_sectors?.us    || []).map(sectorRow).join("");
  const indiaSectors = (chain.level2_sectors?.india || []).map(sectorRow).join("");
  const secondOrder  = (chain.level3_second_order   || []).map(e => `<li class="text-xs text-slate-600">${e}</li>`).join("");

  el.innerHTML = `
    <h3 class="font-bold text-slate-800 mb-4">Causal Chain</h3>

    <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Level 1 — Macro</h4>
    <div class="bg-slate-50 rounded-lg p-3 mb-5">${macroRows}</div>

    <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Level 2 — US Sectors</h4>
    <div class="bg-slate-50 rounded-lg p-3 mb-5">${usSectors || '<p class="text-xs text-slate-400">—</p>'}</div>

    <h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Level 2 — Indian Sectors</h4>
    <div class="bg-orange-50 rounded-lg p-3 mb-5">${indiaSectors || '<p class="text-xs text-slate-400">—</p>'}</div>

    ${secondOrder ? `<h4 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Second-Order Effects</h4>
    <ul class="list-disc list-inside space-y-1.5 mb-5">${secondOrder}</ul>` : ""}

    ${chain.india_macro_summary ? `<div class="bg-orange-50 border border-orange-100 rounded-lg p-4">
      <p class="text-xs font-semibold text-orange-700 mb-1">India Macro Summary</p>
      <p class="text-xs text-orange-900 leading-relaxed">${chain.india_macro_summary}</p>
    </div>` : ""}
  `;
}

/* Sector Rotation — rendered after causal chain */
function renderRotation(chain) {
  const rot = chain?.sector_rotation;
  if (!rot) return;
  const el = document.getElementById("section-rotation");
  el.classList.remove("hidden");

  const list = (arr) => (arr || []).map(s => `<span class="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded">${s}</span>`).join(" ");

  el.innerHTML = `
    <h3 class="font-bold text-slate-800 mb-4">Sector Rotation Signal</h3>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <p class="text-xs font-semibold text-slate-400 uppercase mb-2">US — Capital Leaving</p>
        <div class="flex flex-wrap gap-1.5">${list(rot.from_sectors_us)}</div>
        ${rot.us_etf_proxies?.from ? `<p class="text-xs text-slate-400 mt-2">ETFs: ${rot.us_etf_proxies.from.join(", ")}</p>` : ""}
      </div>
      <div>
        <p class="text-xs font-semibold text-slate-400 uppercase mb-2">US — Capital Rotating Into</p>
        <div class="flex flex-wrap gap-1.5">${list(rot.to_sectors_us)}</div>
        ${rot.us_etf_proxies?.to ? `<p class="text-xs text-slate-400 mt-2">ETFs: ${rot.us_etf_proxies.to.join(", ")}</p>` : ""}
      </div>
      <div>
        <p class="text-xs font-semibold text-slate-400 uppercase mb-2">India — Capital Leaving</p>
        <div class="flex flex-wrap gap-1.5">${list(rot.from_sectors_india)}</div>
      </div>
      <div>
        <p class="text-xs font-semibold text-slate-400 uppercase mb-2">India — Capital Rotating Into</p>
        <div class="flex flex-wrap gap-1.5">${list(rot.to_sectors_india)}</div>
      </div>
    </div>
    ${rot.rotation_timeline ? `<p class="text-xs text-slate-500 mt-3">Timeline: ${rot.rotation_timeline}</p>` : ""}
  `;
}

/* Stock cards */
function stockCard(s, direction) {
  const dirCls = direction === "BUY"  ? "bg-emerald-500" :
                 direction === "SELL" ? "bg-red-500" : "bg-amber-400";
  const durCls = DUR_COLOURS[s.duration_type] || "bg-slate-100 text-slate-600 border-slate-200";
  const convDot = s.conviction === "High" ? "bg-emerald-400" : s.conviction === "Medium" ? "bg-amber-400" : "bg-slate-300";

  const detailRows = [
    s.revenue_exposure    ? ["Exposure",      s.revenue_exposure]    : null,
    s.india_specific_factor ? ["India Factor", s.india_specific_factor] : null,
    s.financial_health    ? ["Balance Sheet", s.financial_health]    : null,
    s.valuation_context   ? ["Valuation",     s.valuation_context]   : null,
  ].filter(Boolean).map(([k, v]) =>
    `<div class="flex gap-2 text-xs py-1.5 border-b border-slate-100 last:border-0">
      <span class="font-semibold text-slate-400 w-24 shrink-0">${k}</span>
      <span class="text-slate-600">${v}</span>
    </div>`
  ).join("");

  const risks = (s.risks || []).map(r =>
    `<span class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded">${r}</span>`
  ).join(" ");

  const watchContent = s.watch_reason ? `
    <p class="text-xs text-slate-600 mt-2">${s.watch_reason}</p>
    ${s.trigger_to_buy  ? `<p class="text-xs text-emerald-600 mt-1">▲ Buy if: ${s.trigger_to_buy}</p>` : ""}
    ${s.trigger_to_sell ? `<p class="text-xs text-red-500 mt-1">▼ Sell if: ${s.trigger_to_sell}</p>` : ""}
  ` : `
    <p class="text-xs text-slate-600 mt-2 leading-relaxed">${s.thesis || ""}</p>
    ${detailRows ? `<div class="mt-3">${detailRows}</div>` : ""}
    ${s.confirmation_trigger ? `<div class="mt-3 bg-emerald-50 rounded p-2 text-xs"><span class="font-semibold text-emerald-700">Confirmation: </span><span class="text-emerald-800">${s.confirmation_trigger}</span></div>` : ""}
    ${s.invalidation_condition ? `<div class="mt-2 bg-red-50 rounded p-2 text-xs"><span class="font-semibold text-red-600">Invalidation: </span><span class="text-red-700">${s.invalidation_condition}</span></div>` : ""}
    ${risks ? `<div class="mt-2 flex flex-wrap gap-1.5">${risks}</div>` : ""}
  `;

  return `
    <div class="border border-slate-200 rounded-lg p-4">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-white text-xs font-bold px-2 py-0.5 rounded ${dirCls}">${direction}</span>
        <span class="font-bold text-slate-900 text-sm">${s.ticker}</span>
        <span class="text-slate-500 text-xs">${s.name || ""}</span>
        <div class="ml-auto flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full ${convDot}"></span>
          <span class="text-xs text-slate-500">${s.conviction || ""}</span>
          ${s.duration_type ? `<span class="text-xs border px-2 py-0.5 rounded-full ${durCls}">${s.duration_type}</span>` : ""}
        </div>
      </div>
      ${s.sector ? `<p class="text-xs text-slate-400 mb-2">${s.sector}</p>` : ""}
      ${watchContent}
    </div>
  `;
}

function renderStocks(market, data) {
  const el   = document.getElementById(`section-${market}`);
  const flag = market === "us" ? "🇺🇸" : "🇮🇳";
  const name = market === "us" ? "US Markets (NYSE / NASDAQ)" : "Indian Markets (NSE / BSE)";
  el.classList.remove("hidden");

  const buys   = (data.strong_buy  || []).map(s => stockCard(s, "BUY")).join("");
  const sells  = (data.strong_sell || []).map(s => stockCard(s, "SELL")).join("");
  const watchl = (data.watchlist   || []).map(s => stockCard(s, "WATCH")).join("");

  el.innerHTML = `
    <h3 class="font-bold text-slate-800 mb-4">${flag} ${name}</h3>

    ${buys ? `<div class="mb-5">
      <p class="text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-2">Strong Buy</p>
      <div class="space-y-3">${buys}</div>
    </div>` : ""}

    ${sells ? `<div class="mb-5">
      <p class="text-xs font-semibold text-red-500 uppercase tracking-wider mb-2">Strong Sell / Avoid</p>
      <div class="space-y-3">${sells}</div>
    </div>` : ""}

    ${watchl ? `<div>
      <p class="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-2">Watch List (awaiting confirmation)</p>
      <div class="space-y-3">${watchl}</div>
    </div>` : ""}
  `;

  if (market === "india" && finalResult?.causal_chain) {
    renderRotation(finalResult.causal_chain);
  }
}

/* Macro Overlay */
function renderMacro(m) {
  if (!m || !Object.keys(m).length) return;
  const el = document.getElementById("section-macro");
  el.classList.remove("hidden");

  const revisions = (m.revised_conclusions || []).map(r =>
    `<li class="text-xs text-slate-600">${r}</li>`
  ).join("");

  el.innerHTML = `
    <h3 class="font-bold text-slate-800 mb-4">Macro Regime Overlay</h3>
    <div class="grid grid-cols-2 gap-3 mb-4">
      ${[
        ["Rate Environment", m.rate_environment_impact],
        ["Market Regime",    m.market_regime_impact],
        ["USD / INR",        m.usd_impact],
        ["Sentiment",        m.sentiment_baseline],
      ].filter(([,v]) => v).map(([k, v]) =>
        `<div class="bg-slate-50 rounded-lg p-3">
          <p class="text-xs font-semibold text-slate-500 mb-1">${k}</p>
          <p class="text-xs text-slate-700">${v}</p>
        </div>`
      ).join("")}
    </div>
    ${m.recent_correlated_events ? `<p class="text-xs text-slate-500 mb-3"><strong>Recent correlations:</strong> ${m.recent_correlated_events}</p>` : ""}
    ${revisions ? `<div class="mb-3"><p class="text-xs font-semibold text-slate-500 mb-1">Revised Conclusions</p><ul class="list-disc list-inside space-y-1">${revisions}</ul></div>` : ""}
    ${m.macro_summary ? `<div class="bg-indigo-50 border border-indigo-100 rounded-lg p-3 text-xs text-indigo-900">${m.macro_summary}</div>` : ""}
  `;
}

/* Final Synthesis */
function renderSynthesis(s) {
  if (!s || !Object.keys(s).length) return;
  const el = document.getElementById("section-synthesis");
  el.classList.remove("hidden");

  const top3 = (s.top_3_trades || []).map((t, i) => `
    <div class="flex gap-3 p-4 ${i === 0 ? "bg-indigo-50 border-indigo-200" : "bg-slate-50 border-slate-200"} border rounded-lg">
      <span class="text-2xl font-black ${i === 0 ? "text-indigo-300" : "text-slate-200"}">${t.rank}</span>
      <div>
        <p class="text-sm font-bold text-slate-800">${t.trade} <span class="text-xs font-normal text-slate-500">(${t.market}, ${t.time_horizon})</span></p>
        <p class="text-xs text-slate-600 mt-0.5">${t.rationale}</p>
        <p class="text-xs text-red-500 mt-1">Risk: ${t.key_risk}</p>
      </div>
    </div>
  `).join("");

  const table = (s.duration_summary_table || []).map(r => {
    const dirCls = r.direction === "BUY" ? "text-emerald-600 font-bold" :
                   r.direction === "SELL" ? "text-red-500 font-bold" : "text-amber-600 font-bold";
    const mktFlag = r.market === "India" ? "🇮🇳" : "🇺🇸";
    return `<tr class="border-b border-slate-100">
      <td class="py-2 px-3 text-xs font-mono text-slate-700">${mktFlag} ${r.ticker}</td>
      <td class="py-2 px-3 text-xs text-slate-600">${r.company || ""}</td>
      <td class="py-2 px-3 text-xs ${dirCls}">${r.direction}</td>
      <td class="py-2 px-3 text-xs text-slate-500">${r.duration || ""}</td>
      <td class="py-2 px-3 text-xs text-slate-500">${r.conviction || ""}</td>
      <td class="py-2 px-3 text-xs text-slate-500">${r.confirmation_trigger || ""}</td>
    </tr>`;
  }).join("");

  el.innerHTML = `
    <!-- What Market Gets Wrong — hero section -->
    <div class="bg-gradient-to-br from-slate-900 to-indigo-950 rounded-xl p-6 mb-6 text-white">
      <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wider mb-3">What The Market Will Get Wrong</p>
      ${s.what_market_gets_wrong?.overreaction ? `
        <div class="mb-4">
          <p class="text-xs font-semibold text-amber-300 mb-1">Over-reaction (Contrarian trade)</p>
          <p class="text-sm text-slate-200 leading-relaxed">${s.what_market_gets_wrong.overreaction}</p>
        </div>` : ""}
      ${s.what_market_gets_wrong?.underreaction ? `
        <div class="mb-4">
          <p class="text-xs font-semibold text-emerald-300 mb-1">Under-reaction (Patient trade)</p>
          <p class="text-sm text-slate-200 leading-relaxed">${s.what_market_gets_wrong.underreaction}</p>
        </div>` : ""}
      ${s.what_market_gets_wrong?.india_specific_mispricing ? `
        <div>
          <p class="text-xs font-semibold text-orange-300 mb-1">🇮🇳 India-Specific Mispricing</p>
          <p class="text-sm text-slate-200 leading-relaxed">${s.what_market_gets_wrong.india_specific_mispricing}</p>
        </div>` : ""}
    </div>

    <!-- Top 3 trades -->
    ${top3 ? `<div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 mb-6">
      <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Top 3 Highest-Conviction Trades</p>
      <div class="space-y-3">${top3}</div>
    </div>` : ""}

    <!-- Duration summary table -->
    ${table ? `<div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 mb-6 overflow-x-auto">
      <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Duration Summary Table</p>
      <table class="w-full text-left">
        <thead><tr class="border-b border-slate-200">
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Ticker</th>
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Company</th>
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Direction</th>
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Duration</th>
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Conviction</th>
          <th class="pb-2 px-3 text-xs text-slate-400 font-semibold">Confirmation Trigger</th>
        </tr></thead>
        <tbody>${table}</tbody>
      </table>
    </div>` : ""}

    <!-- Closing note -->
    ${s.closing_note ? `<div class="bg-slate-50 rounded-xl border border-slate-200 p-5 mb-6">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Honest Disclaimer</p>
      <p class="text-sm text-slate-600 leading-relaxed">${s.closing_note}</p>
    </div>` : ""}

    <!-- Overall verdict -->
    ${s.overall_verdict ? `<div class="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
      <p class="text-xs font-semibold text-indigo-500 uppercase tracking-wider mb-2">Executive Summary</p>
      <p class="text-sm text-indigo-900 leading-relaxed">${s.overall_verdict}</p>
    </div>` : ""}
  `;
}

/* Completion + error ──────────────────────────────────────────────────────── */

function onComplete(result) {
  finalResult = result;
  updateStatusBadge("completed");
  document.getElementById("progress-panel").classList.add("hidden");
  document.getElementById("results-panel").classList.remove("hidden");

  // Re-render all sections from final result (in case events were batched)
  if (result.classification)  renderClassification(result.classification);
  if (result.analogues)       renderAnalogues(result.analogues);
  if (result.causal_chain)  { renderCausalChain(result.causal_chain); renderRotation(result.causal_chain); }
  if (result.us_stocks)       renderStocks("us", result.us_stocks);
  if (result.india_stocks)    renderStocks("india", result.india_stocks);
  if (result.macro_overlay)   renderMacro(result.macro_overlay);
  if (result.synthesis)       renderSynthesis(result.synthesis);
}

function onError(msg) {
  updateStatusBadge("failed");
  clearInterval(pollTimer);
  const ep = document.getElementById("error-panel");
  ep.classList.remove("hidden");
  ep.textContent = `Analysis failed: ${msg}`;
}

function updateStatusBadge(status) {
  const b = document.getElementById("status-badge");
  b.className = `badge-${status} text-xs font-semibold px-2.5 py-1 rounded-full`;
  b.textContent = status === "completed" ? "Complete" : status === "failed" ? "Failed" : "Running";
}
