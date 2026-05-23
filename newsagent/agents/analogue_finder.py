"""Agent 2 — Historical Analogue Finder (Sonnet + seed memory)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_deep_llm
from newsagent.memory import find_relevant_events, format_for_prompt

SYSTEM = """You are a market historian and financial analyst specialising in how major news events
have historically impacted global financial markets, with specific expertise in both US (NYSE/NASDAQ)
and Indian (NSE/BSE) equity markets.

You have been given a VERIFIED HISTORICAL MEMORY of major market events with actual outcomes
(specific index moves, stock names, % changes, India-specific reactions, and what the market
got wrong). Use this memory as your primary factual reference. You may supplement with your
own broader knowledge but DO NOT contradict the provided verified data.

Your task: find 2–3 historical events that are structurally similar to the current event,
and extract precise lessons about how markets behaved — including what the market got WRONG
in its initial reaction.

Respond ONLY with a JSON array. Each element must follow this schema:
{
  "name": "Event name and year (e.g. 'Gulf War 1990–91')",
  "similarity_explanation": "Why this is structurally similar to the current event (2-3 sentences)",
  "market_reaction_5d": {
    "us_indices": "What S&P 500 / NASDAQ did in first 5 days",
    "indian_indices": "What Nifty 50 / Sensex did in first 5 days (if data available, else extrapolate)",
    "key_sectors_up": ["sectors that went up"],
    "key_sectors_down": ["sectors that went down"]
  },
  "market_reaction_30d": {
    "us_indices": "30-day reaction",
    "indian_indices": "30-day reaction for Indian markets",
    "trend_summary": "1-sentence summary of the 30-day trend"
  },
  "market_reaction_6m": {
    "us_indices": "6-month reaction",
    "indian_indices": "6-month reaction for Indian markets",
    "trend_summary": "1-sentence summary of 6-month trend"
  },
  "initial_mispricing": "What the market got wrong in its first reaction — the specific mispricing",
  "correct_trade": "What the right trade turned out to be in hindsight, with specific examples",
  "india_specific_lesson": "What India-specific lesson applies — how Indian markets diverged from global reaction if at all",
  "divergence_from_current": "Where the current situation differs from this historical analogue — important caveats"
}

If no close analogue exists, use partial analogues and explicitly flag where they differ."""


def run_analogue_finder(news_text: str, classification: dict) -> list:
    llm = get_deep_llm()

    # Pull relevant historical events from seed memory
    relevant_events = find_relevant_events(classification, news_text)
    memory_context  = format_for_prompt(relevant_events)

    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Find historical analogues for this event.

NEWS EVENT:
{news_text}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

VERIFIED HISTORICAL MEMORY (use this as your primary reference for actual market data):
{memory_context}

Instructions:
1. Prioritise analogues from the verified memory above where they are structurally similar.
2. You may include additional analogues from your broader knowledge if highly relevant —
   but clearly note these are from your training knowledge, not the verified memory.
3. For each analogue, use the actual verified data (index moves, stock names, % changes)
   from the memory wherever available. Do not invent numbers.

Return a JSON array of 2–3 historical analogues."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    if isinstance(result, list):
        return result
    return []
