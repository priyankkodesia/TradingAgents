"""News analysis pipeline — runs all 7 agents sequentially and emits DB events."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from newsagent.agents.analogue_finder import run_analogue_finder
from newsagent.agents.causal_chain import run_causal_chain
from newsagent.agents.classifier import run_classifier
from newsagent.agents.india_analyst import run_india_analyst
from newsagent.agents.macro_overlay import run_macro_overlay
from newsagent.agents.synthesizer import run_synthesizer
from newsagent.agents.us_analyst import run_us_analyst

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="newsanalysis")

# These are imported lazily to avoid circular imports at module load time.
def _db():
    from web.database import add_news_event, update_news_analysis_status
    return add_news_event, update_news_analysis_status


def submit_news_analysis(analysis_id: str, news_text: str) -> None:
    _executor.submit(_run, analysis_id, news_text)


def _emit(analysis_id: str, event_type: str, data: dict) -> None:
    add_event, _ = _db()
    add_event(analysis_id, event_type, data)


def _step(analysis_id: str, key: str, label: str, fn, *args):
    """Run one agent step, emit started/done events, return result."""
    _emit(analysis_id, "agent_started", {"agent": key, "label": label})
    try:
        result = fn(*args)
        _emit(analysis_id, "agent_done", {"agent": key, "label": label, "result": result})
        return result
    except Exception as exc:
        _emit(analysis_id, "agent_error", {"agent": key, "label": label, "error": str(exc)})
        return None


def _run(analysis_id: str, news_text: str) -> None:
    _, update_status = _db()
    update_status(analysis_id, "running")

    try:
        # Agent 1 — Classify
        classification = _step(
            analysis_id, "classifier", "Classifying event type & scope…",
            run_classifier, news_text,
        ) or {}

        # Agent 2 — Historical analogues
        analogues = _step(
            analysis_id, "analogues", "Finding historical analogues…",
            run_analogue_finder, news_text, classification,
        ) or []

        # Agent 3 — Causal chain
        causal_chain = _step(
            analysis_id, "causal_chain", "Mapping macro → sector → stock causal chain…",
            run_causal_chain, news_text, classification, analogues,
        ) or {}

        # Agent 4 — US stocks (parallel with Agent 5 would be nice but keep simple for now)
        us_stocks = _step(
            analysis_id, "us_analyst", "Analysing US market impact & stock picks…",
            run_us_analyst, news_text, classification, causal_chain,
        ) or {"strong_buy": [], "strong_sell": [], "watchlist": []}

        # Agent 5 — India stocks
        india_stocks = _step(
            analysis_id, "india_analyst", "Analysing Indian market impact & NSE stock picks…",
            run_india_analyst, news_text, classification, causal_chain,
        ) or {"strong_buy": [], "strong_sell": [], "watchlist": []}

        # Agent 6 — Macro overlay
        macro_overlay = _step(
            analysis_id, "macro_overlay", "Applying macro regime overlay…",
            run_macro_overlay, news_text, classification, causal_chain, us_stocks, india_stocks,
        ) or {}

        # Agent 7 — Final synthesis
        synthesis = _step(
            analysis_id, "synthesizer", "Synthesising final verdict…",
            run_synthesizer, news_text, classification, analogues,
            causal_chain, us_stocks, india_stocks, macro_overlay,
        ) or {}

        full_result = {
            "classification": classification,
            "analogues": analogues,
            "causal_chain": causal_chain,
            "us_stocks": us_stocks,
            "india_stocks": india_stocks,
            "macro_overlay": macro_overlay,
            "synthesis": synthesis,
        }

        _emit(analysis_id, "complete", {"result": full_result})
        update_status(analysis_id, "completed", result=full_result)

    except Exception as exc:
        _emit(analysis_id, "error", {"message": str(exc)})
        update_status(analysis_id, "failed", error=str(exc))
