/* HillTrade — analysis page real-time updater */

/* eslint-disable no-undef */

function initAnalysisPage() {
  const ANALYSIS_ID     = window.ANALYSIS_ID;
  const SELECTED        = window.SELECTED_ANALYSTS || [];
  const initialStatus   = window.INITIAL_STATUS;
  const initialRating   = window.INITIAL_RATING;
  const initialError    = window.INITIAL_ERROR;

  // ── State ─────────────────────────────────────────────────────────────
  let lastEventId = 0;
  let isDone = false;
  let startTime = Date.now();
  let elapsedInterval = null;

  const agentStatus = {};       // agent name → status string
  const reportSections = {};    // section key → markdown string

  // Agent table structure matching the CLI layout
  const TEAMS = [
    { team: 'Analyst Team', agents: ['Market Analyst', 'Sentiment Analyst', 'News Analyst', 'Fundamentals Analyst'] },
    { team: 'Research Team', agents: ['Bull Researcher', 'Bear Researcher', 'Research Manager'] },
    { team: 'Trading', agents: ['Trader'] },
    { team: 'Risk Mgmt', agents: ['Aggressive Analyst', 'Conservative Analyst', 'Neutral Analyst'] },
    { team: 'Portfolio', agents: ['Portfolio Manager'] },
  ];

  const ANALYST_MAP = {
    market: 'Market Analyst', social: 'Sentiment Analyst',
    news: 'News Analyst', fundamentals: 'Fundamentals Analyst',
  };

  const SECTION_LABELS = {
    market_report:         'Market Analysis',
    sentiment_report:      'Sentiment Analysis',
    news_report:           'News Analysis',
    fundamentals_report:   'Fundamentals Analysis',
    investment_plan:       'Research Team Decision',
    trader_investment_plan: 'Trading Plan',
    final_trade_decision:  'Portfolio Manager Decision',
  };

  const SECTION_ORDER = Object.keys(SECTION_LABELS);

  // Determine which agents to show based on selected analysts
  const selectedAnalysts = new Set(SELECTED.map(s => s.toLowerCase()));
  const visibleAgents = new Set();
  TEAMS.forEach(({ agents }) => agents.forEach(a => visibleAgents.add(a)));
  // filter out non-selected analyst agents
  Object.entries(ANALYST_MAP).forEach(([key, name]) => {
    if (!selectedAnalysts.has(key)) visibleAgents.delete(name);
  });

  // init all agent statuses to pending
  visibleAgents.forEach(a => { agentStatus[a] = 'pending'; });

  // ── DOM refs ──────────────────────────────────────────────────────────
  const agentTbody    = document.getElementById('agent-tbody');
  const reportsEl     = document.getElementById('reports-container');
  const waitingMsg    = document.getElementById('waiting-msg');
  const statusBadge   = document.getElementById('status-badge');
  const statusText    = document.getElementById('status-text');
  const elapsedEl     = document.getElementById('elapsed-timer');
  const ratingBanner  = document.getElementById('rating-banner');
  const ratingText    = document.getElementById('rating-text');
  const errorPanel    = document.getElementById('error-panel');
  const errorMsg      = document.getElementById('error-msg');
  const stLlm         = document.getElementById('st-llm');
  const stTool        = document.getElementById('st-tool');
  const stIn          = document.getElementById('st-in');
  const stOut         = document.getElementById('st-out');

  // ── Helpers ───────────────────────────────────────────────────────────
  function fmtTokens(n) { return n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n); }

  function fmtElapsed(ms) {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  function statusClass(s) {
    return { completed: 'badge-completed', running: 'badge-running',
             pending: 'badge-pending', failed: 'badge-failed', in_progress: 'badge-running' }[s] || 'badge-pending';
  }

  function ratingClass(r) {
    return { Buy: 'badge-buy', Overweight: 'badge-overweight', Hold: 'badge-hold',
             Underweight: 'badge-underweight', Sell: 'badge-sell' }[r] || '';
  }

  // ── Render agent table ────────────────────────────────────────────────
  function renderAgentTable() {
    const rows = [];
    TEAMS.forEach(({ team, agents }) => {
      const vis = agents.filter(a => visibleAgents.has(a));
      if (!vis.length) return;
      vis.forEach((agent, i) => {
        const s = agentStatus[agent] || 'pending';
        const sc = statusClass(s);
        const spinner = (s === 'in_progress' || s === 'running')
          ? '<span class="spinner" style="width:10px;height:10px;border-width:1.5px;margin-right:4px"></span>'
          : '';
        rows.push(`
          <tr class="hover:bg-slate-50/40">
            <td class="px-3 py-2 text-slate-400">${i === 0 ? team : ''}</td>
            <td class="px-3 py-2 text-slate-700 text-xs">${agent}</td>
            <td class="px-3 py-2 text-center">
              <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${sc}">
                ${spinner}${s}
              </span>
            </td>
          </tr>`);
      });
    });
    agentTbody.innerHTML = rows.join('');
  }

  // ── Render report section card ────────────────────────────────────────
  function renderReports() {
    const hasAny = SECTION_ORDER.some(k => reportSections[k]);
    if (hasAny && waitingMsg) waitingMsg.style.display = 'none';

    SECTION_ORDER.forEach(section => {
      const content = reportSections[section];
      const label   = SECTION_LABELS[section];
      const elId    = `report-${section}`;
      let card      = document.getElementById(elId);

      if (!content) return;

      if (!card) {
        card = document.createElement('div');
        card.id = elId;
        card.className = 'bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden';
        // Insert in order
        const idx = SECTION_ORDER.indexOf(section);
        let inserted = false;
        for (let i = idx + 1; i < SECTION_ORDER.length; i++) {
          const next = document.getElementById(`report-${SECTION_ORDER[i]}`);
          if (next) { reportsEl.insertBefore(card, next); inserted = true; break; }
        }
        if (!inserted) reportsEl.appendChild(card);
      }

      const iconMap = {
        market_report: '📈', sentiment_report: '💬', news_report: '📰',
        fundamentals_report: '📊', investment_plan: '⚖️',
        trader_investment_plan: '💼', final_trade_decision: '🏦',
      };
      const icon = iconMap[section] || '📄';

      card.innerHTML = `
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-slate-800">${icon} ${label}</h3>
          <button onclick="copySection('${section}')"
            class="text-xs text-slate-400 hover:text-slate-600 transition" title="Copy to clipboard">
            Copy
          </button>
        </div>
        <div class="px-5 py-4 prose-report max-h-[28rem] overflow-y-auto" id="report-body-${section}">
          ${marked.parse ? marked.parse(content) : content}
        </div>`;
    });
  }

  window.copySection = function(section) {
    const content = reportSections[section];
    if (content) navigator.clipboard.writeText(content).catch(() => {});
  };

  // ── Update status badge + rating banner ───────────────────────────────
  function setStatus(status) {
    const sc = statusClass(status);
    statusBadge.className = `inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold ${sc}`;
    const showSpinner = (status === 'running' || status === 'pending');
    statusBadge.innerHTML = `
      ${showSpinner ? '<span class="spinner"></span>' : ''}
      <span>${status}</span>`;
  }

  function showRating(rating) {
    if (!rating || !ratingBanner) return;
    const rc = ratingClass(rating);
    ratingBanner.className = `mb-6 p-4 rounded-2xl border flex items-center gap-4 ${rc}`;
    ratingBanner.style.display = '';
    if (ratingText) ratingText.textContent = rating;
    ratingBanner.classList.remove('hidden');
  }

  function showError(msg) {
    if (!errorPanel) return;
    errorPanel.classList.remove('hidden');
    if (errorMsg) errorMsg.textContent = msg;
  }

  // ── Elapsed timer ─────────────────────────────────────────────────────
  function startTimer() {
    if (elapsedEl) {
      elapsedEl.classList.remove('hidden');
      elapsedInterval = setInterval(() => {
        elapsedEl.textContent = '⏱ ' + fmtElapsed(Date.now() - startTime);
      }, 1000);
    }
  }

  function stopTimer() {
    clearInterval(elapsedInterval);
    if (elapsedEl) elapsedEl.textContent = '⏱ ' + fmtElapsed(Date.now() - startTime) + ' (done)';
  }

  // ── Process a single DB event ─────────────────────────────────────────
  function processEvent(ev) {
    lastEventId = Math.max(lastEventId, ev.id || 0);
    let data;
    try { data = typeof ev.data === 'string' ? JSON.parse(ev.data) : ev.data; }
    catch { return; }

    switch (ev.event_type) {
      case 'agent_status':
        if (visibleAgents.has(data.agent)) {
          agentStatus[data.agent] = data.status;
          renderAgentTable();
        }
        break;
      case 'report_section':
        reportSections[data.section] = data.content;
        renderReports();
        break;
      case 'stats':
        if (stLlm)  stLlm.textContent  = data.llm_calls  ?? '—';
        if (stTool) stTool.textContent = data.tool_calls ?? '—';
        if (stIn)   stIn.textContent   = fmtTokens(data.tokens_in  || 0);
        if (stOut)  stOut.textContent  = fmtTokens(data.tokens_out || 0);
        break;
      case 'complete':
        isDone = true;
        setStatus('completed');
        stopTimer();
        if (data.decision) showRating(data.decision);
        renderAgentTable();
        break;
      case 'error':
        isDone = true;
        setStatus('failed');
        stopTimer();
        showError(data.message || 'Unknown error');
        break;
      case 'status':
        if (data.status === 'running') setStatus('running');
        break;
    }
  }

  // ── Polling ───────────────────────────────────────────────────────────
  async function poll() {
    if (isDone) return;
    try {
      const res = await fetch(`/api/analysis/${ANALYSIS_ID}/events?since=${lastEventId}`);
      if (!res.ok) return;
      const result = await res.json();
      (result.events || []).forEach(processEvent);
      if (result.status === 'completed' || result.status === 'failed') {
        isDone = true;
        clearInterval(pollInterval);
        setStatus(result.status);
        stopTimer();
        if (result.rating) showRating(result.rating);
        if (result.error)  showError(result.error);
      }
    } catch { /* network hiccup, retry next tick */ }
  }

  let pollInterval = null;

  // ── Boot ──────────────────────────────────────────────────────────────
  renderAgentTable();
  renderReports();

  // Replay initial events (already in DB when page loaded)
  (window.INITIAL_EVENTS || []).forEach(processEvent);

  if (initialStatus === 'completed' || initialStatus === 'failed') {
    isDone = true;
    setStatus(initialStatus);
    if (initialRating) showRating(initialRating);
    if (initialError)  showError(initialError);
    if (waitingMsg && Object.values(reportSections).some(Boolean)) {
      waitingMsg.style.display = 'none';
    }
  } else {
    setStatus(initialStatus || 'pending');
    startTimer();
    pollInterval = setInterval(poll, 1500);
  }
}
