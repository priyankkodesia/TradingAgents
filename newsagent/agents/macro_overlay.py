"""Agent 6 — Macro Overlay (Haiku, adjusts conclusions for current regime)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_quick_llm

SYSTEM = """You are a macro strategist. Given a completed news event analysis, you apply
the current macro context as a final overlay — identifying where the prevailing macro regime
amplifies, dampens, or reverses the base case analysis.

Consider:
1. Interest rate cycle (Fed tightening/easing affects equity multiples and emerging market flows)
2. Market regime (risk-on vs risk-off environment affects how news propagates)
3. USD cycle (strong USD hurts emerging markets including India, affects multinationals)
4. Recent correlated events (is this event compounding or offsetting recent developments?)
5. Market sentiment baseline (complacent markets amplify negative news; fearful markets are more resilient)

Respond ONLY with a valid JSON object:
{
  "rate_environment_impact": "How current rate cycle affects this event's market impact",
  "market_regime_impact": "Risk-on/off context and how it changes the analysis",
  "usd_impact": "Dollar cycle effect, particularly on Indian markets and multinationals",
  "recent_correlated_events": "Any recent events this compounds or offsets",
  "sentiment_baseline": "Is the market complacent or fearful? Effect on this event",
  "revised_conclusions": [
    "Conclusion 1 from base analysis that needs upgrading due to macro context",
    "Conclusion 2 that needs downgrading",
    "India-specific macro revision if any"
  ],
  "macro_summary": "2-sentence overall macro overlay verdict — does the current macro environment make this event MORE or LESS impactful than the historical base case suggests?"
}"""


def run_macro_overlay(
    news_text: str,
    classification: dict,
    causal_chain: dict,
    us_stocks: dict,
    india_stocks: dict,
) -> dict:
    llm = get_quick_llm()
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Apply macro overlay to this completed analysis.

NEWS EVENT:
{news_text}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

SECTOR IMPACTS:
US sectors: {json.dumps(causal_chain.get("level2_sectors", {}).get("us", []), indent=2)}
India sectors: {json.dumps(causal_chain.get("level2_sectors", {}).get("india", []), indent=2)}

TOP US BUY PICKS: {[s.get("ticker") for s in us_stocks.get("strong_buy", [])[:3]]}
TOP INDIA BUY PICKS: {[s.get("ticker") for s in india_stocks.get("strong_buy", [])[:3]]}

Apply the current macro regime overlay and return JSON."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    return result if isinstance(result, dict) else {}
