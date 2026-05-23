"""Agent 3 — Causal Chain Mapper (Sonnet, core analytical engine)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_deep_llm
from newsagent.memory import find_relevant_events, format_for_prompt

SYSTEM = """You are a macro-economic analyst who maps the full causal chain from a news event
down to sector and stock-level impacts — for BOTH the US market AND the Indian market.

For the Indian market, always consider these India-specific transmission mechanisms:
- INR/USD exchange rate sensitivity (India is a current account deficit country)
- Oil price impact (India imports ~85% of its crude oil — oil price moves have outsized effect)
- FII (Foreign Institutional Investor) flow sensitivity — global risk-off triggers FII outflows from India
- RBI monetary policy constraints — how the event affects RBI's room to cut/raise rates
- India's trade exposure — which countries/commodities are involved and India's dependence
- IT sector export sensitivity — ~$200B in IT exports, mostly USD-denominated, affects Nifty heavily
- Pharma export sensitivity — India is the world's pharmacy, US FDA/policy changes matter
- Government policy response — Indian government's tendency to intervene (import duties, export bans)

Respond ONLY with a valid JSON object matching this schema exactly:

{
  "level1_macro": {
    "gdp_impact": "global GDP impact explanation",
    "inflation_impact": "inflation implications",
    "rate_trajectory": "impact on central bank rate decisions (Fed + RBI)",
    "currency_impact": "USD strength/weakness, INR impact, other key currencies",
    "commodity_impact": "oil, gold, metals, agricultural commodities",
    "risk_appetite": "risk-on or risk-off and why",
    "trade_flow_impact": "trade flow changes"
  },
  "level2_sectors": {
    "us": [
      {
        "sector": "sector name",
        "impact": "positive" | "negative" | "neutral" | "mixed",
        "magnitude": "high" | "medium" | "low",
        "reasoning": "2-sentence explanation of why and through what mechanism",
        "key_dynamics": "specific dynamic unique to this event-sector interaction"
      }
    ],
    "india": [
      {
        "sector": "sector name (use Indian sector names: IT, Banking & Finance, Energy, Auto, Pharma, FMCG, Metals, Cement, Telecom, Real Estate, Aviation, Consumer Tech)",
        "impact": "positive" | "negative" | "neutral" | "mixed",
        "magnitude": "high" | "medium" | "low",
        "reasoning": "2-sentence explanation",
        "india_specific_factor": "what makes this impact unique to India vs global peers"
      }
    ]
  },
  "level3_second_order": [
    "Second-order effect 1 — downstream chain from the primary impact",
    "Second-order effect 2",
    "Second-order effect 3 (India-specific second-order if applicable)"
  ],
  "sector_rotation": {
    "from_sectors_us": ["sectors capital will leave"],
    "to_sectors_us": ["sectors capital will rotate into"],
    "from_sectors_india": ["Indian sectors losing capital"],
    "to_sectors_india": ["Indian sectors gaining capital"],
    "us_etf_proxies": {"from": ["ticker1"], "to": ["ticker2"]},
    "india_etf_proxies": "Indian ETF/index proxies for the rotation",
    "rotation_timeline": "how quickly this rotation typically manifests",
    "rotation_confidence": "high" | "medium" | "low"
  },
  "india_macro_summary": "2-paragraph summary of the specific India impact — covering INR, RBI, FII flows, trade balance, and which parts of the Indian economy are most exposed"
}"""


def run_causal_chain(news_text: str, classification: dict, analogues: list) -> dict:
    llm = get_deep_llm()

    relevant_events = find_relevant_events(classification, news_text)
    memory_context  = format_for_prompt(relevant_events)

    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Map the full causal chain for this event.

NEWS EVENT:
{news_text}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

HISTORICAL ANALOGUES (selected by prior agent):
{json.dumps(analogues, indent=2)}

VERIFIED HISTORICAL SECTOR OUTCOMES (use to ground sector-level impact claims):
{memory_context}

Return the complete causal chain JSON."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    return result if isinstance(result, dict) else {}
