"""Agent 7 — Synthesizer (Sonnet, final verdict + what market will get wrong)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_deep_llm

SYSTEM = """You are a senior portfolio strategist writing the final synthesis of a multi-agent
news event analysis. Your most important job is the "What Market Will Get Wrong" section —
this is where the real alpha lies, not in the obvious first-order reactions.

Respond ONLY with a valid JSON object:
{
  "overall_verdict": "3-sentence executive summary: what happened, what it means for markets, and the single most important trade implication",
  "duration_summary_table": [
    {
      "ticker": "TICKER or TICKER.NS",
      "market": "US" or "India",
      "company": "Company name",
      "direction": "BUY|SELL|WATCH",
      "duration": "TEMPORARY|CYCLICAL|STRUCTURAL|FUNDAMENTAL SHIFT",
      "conviction": "High|Medium|Low",
      "confirmation_trigger": "one-line trigger"
    }
  ],
  "what_market_gets_wrong": {
    "overreaction": "What is the market likely to OVER-react to? Where is the panic/euphoria misplaced? Which stocks will be wrongly sold or wrongly bought in the initial wave? This is the contrarian trade.",
    "underreaction": "What is the market likely to UNDER-react to or ignore entirely? What second or third-order effect will take weeks/months to be priced in? This is the patient trade.",
    "india_specific_mispricing": "What India-specific mispricing is most likely? Indian markets are often subject to FII herding behavior and can overshoot in both directions."
  },
  "top_3_trades": [
    {
      "rank": 1,
      "market": "US|India",
      "trade": "TICKER — direction",
      "rationale": "One sentence: the single clearest, highest-conviction trade from this entire analysis",
      "time_horizon": "days|weeks|months",
      "key_risk": "The one thing that could kill this trade"
    }
  ],
  "avoid_list": [
    {
      "ticker": "TICKER or TICKER.NS",
      "market": "US|India",
      "reason": "Why to avoid — not enough edge, too binary, already priced in, etc."
    }
  ],
  "closing_note": "1 paragraph: the honest disclaimer — what this analysis cannot predict, where uncertainty is highest, and what additional information would change the conclusions materially"
}"""


def run_synthesizer(
    news_text: str,
    classification: dict,
    analogues: list,
    causal_chain: dict,
    us_stocks: dict,
    india_stocks: dict,
    macro_overlay: dict,
) -> dict:
    llm = get_deep_llm()

    all_buys = (
        [f"US:{s['ticker']}" for s in us_stocks.get("strong_buy", [])]
        + [f"IN:{s['ticker']}" for s in india_stocks.get("strong_buy", [])]
    )
    all_sells = (
        [f"US:{s['ticker']}" for s in us_stocks.get("strong_sell", [])]
        + [f"IN:{s['ticker']}" for s in india_stocks.get("strong_sell", [])]
    )

    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Synthesize this complete analysis into a final verdict.

NEWS EVENT:
{news_text}

CLASSIFICATION: {json.dumps(classification, indent=2)}

HISTORICAL ANALOGUES: {json.dumps([a.get("name") + ": " + a.get("initial_mispricing", "") for a in analogues], indent=2)}

CAUSAL CHAIN SUMMARY:
- Macro: {json.dumps(causal_chain.get("level1_macro", {}), indent=2)}
- Sector rotation: {json.dumps(causal_chain.get("sector_rotation", {}), indent=2)}

ALL BUY PICKS: {all_buys}
ALL SELL PICKS: {all_sells}
WATCHLIST: {[f"US:{s['ticker']}" for s in us_stocks.get("watchlist", [])] + [f"IN:{s['ticker']}" for s in india_stocks.get("watchlist", [])]}

MACRO OVERLAY: {json.dumps(macro_overlay, indent=2)}

Write the final synthesis JSON."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    return result if isinstance(result, dict) else {}
