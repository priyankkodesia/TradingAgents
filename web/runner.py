"""Background analysis runner — mirrors CLI streaming logic, writes to SQLite."""

import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from cli.stats_handler import StatsCallbackHandler
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

from .database import add_event, get_analysis, update_analysis_status

# ── constants ─────────────────────────────────────────────────────────────────

ANALYST_ORDER = ["market", "social", "news", "fundamentals"]
ANALYST_NAMES = {
    "market": "Market Analyst",
    "social": "Sentiment Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
}
ANALYST_REPORT_KEY = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
}
FIXED_AGENTS = [
    "Bull Researcher", "Bear Researcher", "Research Manager",
    "Trader",
    "Aggressive Analyst", "Conservative Analyst", "Neutral Analyst",
    "Portfolio Manager",
]

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="analysis")


# ── public API ────────────────────────────────────────────────────────────────

def submit_analysis(analysis_id: str, settings: dict) -> None:
    _executor.submit(_run, analysis_id, settings)


# ── internal state tracker ────────────────────────────────────────────────────

class _RunState:
    def __init__(self, selected_analysts: list[str]):
        self.selected = [a.lower() for a in selected_analysts]
        self.agent_status: dict[str, str] = {}
        self.report_sections: dict[str, str | None] = {}
        self._seen_ids: set = set()

        for key in self.selected:
            name = ANALYST_NAMES.get(key)
            if name:
                self.agent_status[name] = "pending"
        for agent in FIXED_AGENTS:
            self.agent_status[agent] = "pending"

        for key in self.selected:
            rkey = ANALYST_REPORT_KEY.get(key)
            if rkey:
                self.report_sections[rkey] = None
        for k in ("investment_plan", "trader_investment_plan", "final_trade_decision"):
            self.report_sections[k] = None


# ── helpers ───────────────────────────────────────────────────────────────────

def _emit_agent(aid: str, state: _RunState, agent: str, status: str) -> None:
    if state.agent_status.get(agent) != status:
        state.agent_status[agent] = status
        add_event(aid, "agent_status", {"agent": agent, "status": status})


def _emit_report(aid: str, state: _RunState, section: str, content: str) -> None:
    if section in state.report_sections and content:
        state.report_sections[section] = content
        add_event(aid, "report_section", {"section": section, "content": content})


def _extract_text(content) -> str | None:
    if not content:
        return None
    if isinstance(content, str):
        return content.strip() or None
    if isinstance(content, dict):
        t = content.get("text", "")
        return t.strip() or None
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", "").strip())
            elif isinstance(item, str):
                parts.append(item.strip())
        return " ".join(p for p in parts if p) or None
    return str(content).strip() or None


def _process_chunk(aid: str, state: _RunState, chunk: dict) -> None:
    # ── messages ──
    for msg in chunk.get("messages", []):
        msg_id = getattr(msg, "id", None)
        if msg_id:
            if msg_id in state._seen_ids:
                continue
            state._seen_ids.add(msg_id)

        text = _extract_text(getattr(msg, "content", None))
        if text:
            if isinstance(msg, HumanMessage):
                mtype = "Control" if text.strip() == "Continue" else "User"
            elif isinstance(msg, ToolMessage):
                mtype = "Data"
            elif isinstance(msg, AIMessage):
                mtype = "Agent"
            else:
                mtype = "System"
            add_event(aid, "message", {"type": mtype, "content": text[:600]})

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc["name"] if isinstance(tc, dict) else tc.name
                args = tc["args"] if isinstance(tc, dict) else tc.args
                add_event(aid, "tool_call", {"name": name, "args": str(args)[:300]})

    # ── analyst reports ──
    found_active = False
    for key in ANALYST_ORDER:
        if key not in state.selected:
            continue
        agent = ANALYST_NAMES[key]
        rkey = ANALYST_REPORT_KEY[key]
        if chunk.get(rkey):
            _emit_report(aid, state, rkey, chunk[rkey])
        has_report = bool(state.report_sections.get(rkey))
        if has_report:
            _emit_agent(aid, state, agent, "completed")
        elif not found_active:
            _emit_agent(aid, state, agent, "in_progress")
            found_active = True

    if not found_active and state.selected:
        if state.agent_status.get("Bull Researcher") == "pending":
            _emit_agent(aid, state, "Bull Researcher", "in_progress")

    # ── research debate ──
    if chunk.get("investment_debate_state"):
        d = chunk["investment_debate_state"]
        bull = (d.get("bull_history") or "").strip()
        bear = (d.get("bear_history") or "").strip()
        judge = (d.get("judge_decision") or "").strip()

        if bull or bear:
            for ag in ["Bull Researcher", "Bear Researcher", "Research Manager"]:
                if state.agent_status.get(ag) == "pending":
                    _emit_agent(aid, state, ag, "in_progress")
        if bull:
            _emit_report(aid, state, "investment_plan", f"### Bull Researcher\n{bull}")
        if bear:
            _emit_report(aid, state, "investment_plan", f"### Bear Researcher\n{bear}")
        if judge:
            _emit_report(aid, state, "investment_plan", f"### Research Manager Decision\n{judge}")
            for ag in ["Bull Researcher", "Bear Researcher", "Research Manager"]:
                _emit_agent(aid, state, ag, "completed")
            _emit_agent(aid, state, "Trader", "in_progress")

    # ── trader ──
    if chunk.get("trader_investment_plan"):
        _emit_report(aid, state, "trader_investment_plan", chunk["trader_investment_plan"])
        if state.agent_status.get("Trader") != "completed":
            _emit_agent(aid, state, "Trader", "completed")
            _emit_agent(aid, state, "Aggressive Analyst", "in_progress")

    # ── risk debate ──
    if chunk.get("risk_debate_state"):
        r = chunk["risk_debate_state"]
        agg = (r.get("aggressive_history") or "").strip()
        con = (r.get("conservative_history") or "").strip()
        neu = (r.get("neutral_history") or "").strip()
        judge = (r.get("judge_decision") or "").strip()

        if agg:
            _emit_agent(aid, state, "Aggressive Analyst", "in_progress")
            _emit_report(aid, state, "final_trade_decision", f"### Aggressive Analyst\n{agg}")
        if con:
            _emit_agent(aid, state, "Conservative Analyst", "in_progress")
            _emit_report(aid, state, "final_trade_decision", f"### Conservative Analyst\n{con}")
        if neu:
            _emit_agent(aid, state, "Neutral Analyst", "in_progress")
            _emit_report(aid, state, "final_trade_decision", f"### Neutral Analyst\n{neu}")
        if judge:
            _emit_report(aid, state, "final_trade_decision", f"### Portfolio Manager\n{judge}")
            for ag in ["Aggressive Analyst", "Conservative Analyst", "Neutral Analyst", "Portfolio Manager"]:
                _emit_agent(aid, state, ag, "completed")


def _build_config(settings: dict) -> dict:
    cfg = DEFAULT_CONFIG.copy()
    cfg["max_debate_rounds"] = int(settings.get("research_depth", 1))
    cfg["max_risk_discuss_rounds"] = int(settings.get("research_depth", 1))
    cfg["llm_provider"] = settings.get("provider", "openai").lower()
    cfg["deep_think_llm"] = settings.get("deep_model", cfg["deep_think_llm"])
    cfg["quick_think_llm"] = settings.get("quick_model", cfg["quick_think_llm"])
    cfg["output_language"] = settings.get("output_language", "English")
    if settings.get("backend_url"):
        cfg["backend_url"] = settings["backend_url"]
    return cfg


# ── main worker ───────────────────────────────────────────────────────────────

def _run(analysis_id: str, settings: dict) -> None:
    try:
        update_analysis_status(analysis_id, "running")
        add_event(analysis_id, "status", {"status": "running"})

        analysts = settings.get("analysts", list(ANALYST_ORDER))
        ticker = settings["ticker"]
        date = settings["analysis_date"]
        config = _build_config(settings)

        stats_cb = StatsCallbackHandler()
        run_state = _RunState(analysts)

        graph = TradingAgentsGraph(
            selected_analysts=analysts,
            config=config,
            debug=True,
            callbacks=[stats_cb],
        )

        init_state = graph.propagator.create_initial_state(ticker, date)
        args = graph.propagator.get_graph_args(callbacks=[stats_cb])

        trace: list[dict] = []
        last_stats_emit = time.time()

        for chunk in graph.graph.stream(init_state, **args):
            _process_chunk(analysis_id, run_state, chunk)
            trace.append(chunk)
            now = time.time()
            if now - last_stats_emit > 3:
                add_event(analysis_id, "stats", stats_cb.get_stats())
                last_stats_emit = now

        # merge final state
        final_state: dict = {}
        for chunk in trace:
            final_state.update(chunk)

        # mark all agents done
        for agent in list(run_state.agent_status):
            add_event(analysis_id, "agent_status", {"agent": agent, "status": "completed"})

        decision = graph.process_signal(final_state.get("final_trade_decision", ""))
        add_event(analysis_id, "stats", stats_cb.get_stats())
        add_event(analysis_id, "complete", {"decision": decision})
        update_analysis_status(
            analysis_id,
            "completed",
            final_decision=final_state.get("final_trade_decision", ""),
            rating=decision,
        )

    except Exception as exc:
        err = str(exc)
        tb = traceback.format_exc()
        add_event(analysis_id, "error", {"message": err, "traceback": tb})
        update_analysis_status(analysis_id, "failed", error=err)
