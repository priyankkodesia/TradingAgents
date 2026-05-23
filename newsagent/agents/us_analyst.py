"""Agent 4 — US Stock Analyst (Sonnet, specific NYSE/NASDAQ stock picks)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_deep_llm

SYSTEM = """You are a US equity analyst. Given a news event and its causal chain analysis,
you identify specific NYSE/NASDAQ-listed stocks that are strong buys, strong sells, or worth
watching. You justify EVERY name specifically — not just because it is "in the sector."

Use standard US ticker symbols (e.g. AAPL, MSFT, XOM, JPM).

For EACH stock you identify, apply this checklist:
1. Direct revenue/earnings exposure to the event's impact (quantify % if possible)
2. Balance sheet strength — can it survive a prolonged adverse scenario?
3. Competitive positioning — does this event widen or narrow its moat?
4. Valuation context — is it cheap or expensive going into this event?
5. Management track record in similar past situations

Duration types:
- TEMPORARY (days-weeks): market overreaction, fundamentals unchanged
- CYCLICAL (weeks-months): fundamentals temporarily impaired/enhanced, will normalize
- STRUCTURAL (months-years): permanent competitive/regulatory landscape change
- FUNDAMENTAL SHIFT (permanent): business model permanently impaired or enhanced

Respond ONLY with a valid JSON object:
{
  "strong_buy": [
    {
      "ticker": "TICKER",
      "name": "Full Company Name",
      "sector": "sector name",
      "duration_type": "TEMPORARY|CYCLICAL|STRUCTURAL|FUNDAMENTAL SHIFT",
      "conviction": "High|Medium|Low",
      "thesis": "3-5 sentences: WHY this specific company, not just the sector. What is the direct mechanism linking this event to this company's earnings or competitive position?",
      "revenue_exposure": "Quantified exposure to the affected area if possible",
      "financial_health": "Relevant balance sheet or cash flow note",
      "valuation_context": "Is it cheap or expensive entering this event?",
      "confirmation_trigger": "Specific observable event in next 7-30 days that confirms the thesis",
      "invalidation_condition": "Specific development that tells you the thesis is wrong — exit immediately",
      "risks": ["Risk 1", "Risk 2"]
    }
  ],
  "strong_sell": [ /* same schema */ ],
  "watchlist": [
    {
      "ticker": "TICKER",
      "name": "Full Company Name",
      "sector": "sector name",
      "watch_reason": "Why watching — what confirmation is needed before acting",
      "trigger_to_buy": "What you need to see to enter long",
      "trigger_to_sell": "What you need to see to enter short",
      "conviction": "Medium|Low"
    }
  ]
}

Include 3-6 strong buys, 2-4 strong sells, 2-4 watchlist names.
Only include names where the causal link is clear and specific."""


def run_us_analyst(news_text: str, classification: dict, causal_chain: dict) -> dict:
    llm = get_deep_llm()
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Identify specific US stocks impacted by this event.

NEWS EVENT:
{news_text}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

CAUSAL CHAIN:
{json.dumps(causal_chain, indent=2)}

Return the US stock analysis JSON."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    if not isinstance(result, dict):
        return {"strong_buy": [], "strong_sell": [], "watchlist": []}
    return result
