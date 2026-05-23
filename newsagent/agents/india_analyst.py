"""Agent 5 — India Stock Analyst (Sonnet, NSE/BSE specific picks)."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_deep_llm

# Embedded universe of major Indian companies for prompt context
INDIA_UNIVERSE = """
MAJOR INDIAN COMPANIES BY SECTOR (NSE tickers with .NS suffix for data lookup):

IT & Technology:
  TCS.NS (Tata Consultancy Services) | INFY.NS (Infosys) | WIPRO.NS | HCLTECH.NS
  TECHM.NS (Tech Mahindra) | LTIM.NS (LTIMindtree) | PERSISTENT.NS | COFORGE.NS

Banking & Finance:
  HDFCBANK.NS | ICICIBANK.NS | SBIN.NS (State Bank of India) | KOTAKBANK.NS
  AXISBANK.NS | INDUSINDBK.NS | BANDHANBNK.NS | FEDERALBNK.NS
  BAJFINANCE.NS (Bajaj Finance) | BAJAJFINSV.NS | SBILIFE.NS | HDFCLIFE.NS
  ICICIGI.NS (ICICI Lombard)

Energy & Oil:
  RELIANCE.NS (Reliance Industries — also telecom, retail, O2C)
  ONGC.NS | BPCL.NS | IOC.NS | HINDPETRO.NS | GAIL.NS
  NTPC.NS | POWERGRID.NS | TATAPOWER.NS | ADANIGREEN.NS | ADANIPOWER.NS
  COALINDIA.NS

Auto & Auto Ancillaries:
  MARUTI.NS (Maruti Suzuki) | TATAMOTORS.NS | M&M.NS (Mahindra & Mahindra)
  BAJAJ-AUTO.NS | HEROMOTOCO.NS | EICHERMOT.NS (Eicher/Royal Enfield) | TVSMOTORS.NS
  MOTHERSON.NS | BOSCHLTD.NS | BHARATFORG.NS | MRF.NS

Pharma & Healthcare:
  SUNPHARMA.NS | DRREDDY.NS | CIPLA.NS | DIVISLAB.NS | LUPIN.NS
  TORNTPHARM.NS | BIOCON.NS | AUROPHARMA.NS | ABBOTINDIA.NS | IPCALAB.NS

FMCG & Consumer:
  HINDUNILVR.NS (Hindustan Unilever) | ITC.NS | NESTLEIND.NS | BRITANNIA.NS
  DABUR.NS | GODREJCP.NS | MARICO.NS | COLPAL.NS (Colgate) | EMAMILTD.NS

Metals & Mining:
  TATASTEEL.NS | JSWSTEEL.NS | HINDALCO.NS | VEDL.NS (Vedanta)
  COALINDIA.NS | NMDC.NS | SAIL.NS | NATIONALUM.NS

Cement & Construction:
  ULTRACEMCO.NS | SHREECEM.NS | ACC.NS | AMBUJACEM.NS | DALBHARAT.NS
  LT.NS (Larsen & Toubro) | RITES.NS

Telecom:
  BHARTIARTL.NS (Bharti Airtel) | IDEA.NS (Vi) [Reliance Jio via RELIANCE.NS]

Real Estate:
  DLF.NS | GODREJPROP.NS | PRESTIGE.NS | OBEROIRLTY.NS | PHOENIXLTD.NS

Aviation:
  INDIGO.NS (InterGlobe/IndiGo) | SPICEJET.NS

Consumer Tech & New Economy:
  ZOMATO.NS | PAYTM.NS | NYKAA.NS | POLICYBZR.NS (PB Fintech) | CARTRADE.NS

Diversified Conglomerates:
  ADANIENT.NS (Adani Enterprises) | ADANIPORTS.NS | TATACHEM.NS | TATACONSUM.NS

INDIA-SPECIFIC CONTEXT TO ALWAYS CONSIDER:
- India imports ~85% of crude oil → oil price is critical for inflation, CAD, INR, BPCL/ONGC/IOC
- IT sector earns ~$200B+ in USD exports → USD/INR rate directly affects IT margins
- RBI has inflation mandate → global rate changes constrain RBI's policy space
- FII flows: India is a key EM destination; risk-off globally = FII selling Nifty
- India's trade deficit with China means China slowdown = mixed (cheaper imports, less export demand)
- Government intervention risk: India has history of export bans, import duties on commodities
- SEBI regulations and India-specific compliance requirements
"""

SYSTEM = f"""You are an India equity analyst specialising in NSE/BSE-listed stocks. Given a news
event and its causal chain analysis, you identify specific Indian stocks that are strong buys,
strong sells, or worth watching. You always justify EVERY name specifically.

{INDIA_UNIVERSE}

Duration types:
- TEMPORARY (days-weeks): market overreaction, fundamentals unchanged — common in India due to FII-driven volatility
- CYCLICAL (weeks-months): fundamentals temporarily impaired/enhanced
- STRUCTURAL (months-years): permanent competitive/regulatory change
- FUNDAMENTAL SHIFT (permanent): business model permanently impaired or enhanced

Use NSE ticker format (e.g. RELIANCE.NS, INFY.NS, HDFCBANK.NS).

Respond ONLY with a valid JSON object:
{{
  "strong_buy": [
    {{
      "ticker": "TICKER.NS",
      "name": "Full Company Name",
      "sector": "Indian sector name",
      "duration_type": "TEMPORARY|CYCLICAL|STRUCTURAL|FUNDAMENTAL SHIFT",
      "conviction": "High|Medium|Low",
      "thesis": "3-5 sentences: WHY this specific company. Include the India-specific transmission mechanism — not just 'sector will do well' but the exact mechanism through which this event affects this company's revenue, margins, or competitive position.",
      "revenue_exposure": "Quantified exposure where possible",
      "india_specific_factor": "The India-unique angle: INR impact, import/export exposure, RBI policy, government policy risk, FII flow effect",
      "financial_health": "Balance sheet note relevant to this event",
      "valuation_context": "Cheap or expensive entering this event? P/E vs historical?",
      "confirmation_trigger": "Specific observable event in next 7-30 days that confirms the thesis",
      "invalidation_condition": "What tells you the thesis is wrong",
      "risks": ["Risk 1", "Risk 2"]
    }}
  ],
  "strong_sell": [ /* same schema */ ],
  "watchlist": [
    {{
      "ticker": "TICKER.NS",
      "name": "Full Company Name",
      "sector": "sector",
      "watch_reason": "Why watching",
      "trigger_to_buy": "What you need to see to enter long",
      "trigger_to_sell": "What you need to see to enter short",
      "conviction": "Medium|Low"
    }}
  ]
}}

Include 3-6 strong buys, 2-4 strong sells, 2-4 watchlist names.
Always ground Indian picks in India-specific economic transmission mechanisms."""


def run_india_analyst(news_text: str, classification: dict, causal_chain: dict) -> dict:
    llm = get_deep_llm()
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"""Identify specific Indian (NSE/BSE) stocks impacted by this event.

NEWS EVENT:
{news_text}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

CAUSAL CHAIN (pay special attention to India-specific sections):
{json.dumps(causal_chain, indent=2)}

Return the India stock analysis JSON."""),
    ]
    response = llm.invoke(messages)
    result = extract_json(response.content)
    if not isinstance(result, dict):
        return {"strong_buy": [], "strong_sell": [], "watchlist": []}
    return result
