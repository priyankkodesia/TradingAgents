"""Agent 1 — Event Classifier (Haiku, fast structured output)."""

from langchain_core.messages import HumanMessage, SystemMessage

from newsagent.llm import extract_json, get_quick_llm

SYSTEM = """You are a financial news event classifier. Your job is to classify a news event
across several dimensions so a downstream analysis pipeline can route it correctly.

Respond ONLY with a valid JSON object — no prose, no markdown explanation outside the code block.

Required JSON schema:
{
  "event_title": "short descriptive title (max 10 words)",
  "event_type": one of ["Geopolitical", "Macroeconomic", "Monetary Policy", "Regulatory",
                        "Natural Disaster", "Pandemic", "Corporate", "Technology Shift",
                        "Black Swan", "Social/Political"],
  "scope": one of ["Global", "Regional", "National", "Sector-specific", "Company-specific"],
  "novelty": one of ["Completely new information", "Escalation of known risk",
                     "Resolution of known risk", "Confirmation of expectation"],
  "speed": one of ["Immediate (hours)", "Short-term (days-weeks)",
                   "Medium-term (months)", "Structural (years)"],
  "already_priced_in": true or false,
  "priced_in_note": "explanation if already_priced_in is true, else null",
  "event_summary": "2-sentence factual summary of the event and why it matters to markets",
  "primary_affected_regions": ["list", "of", "regions"],
  "us_relevance": one of ["High", "Medium", "Low"],
  "india_relevance": one of ["High", "Medium", "Low"],
  "india_relevance_reason": "one sentence on why/how this affects India specifically"
}"""


_FALLBACK = {
    "event_title": "Unknown Event",
    "event_type": "Macroeconomic",
    "scope": "Global",
    "novelty": "Completely new information",
    "speed": "Short-term (days-weeks)",
    "already_priced_in": False,
    "priced_in_note": None,
    "event_summary": "",
    "primary_affected_regions": ["Global"],
    "us_relevance": "Medium",
    "india_relevance": "Medium",
    "india_relevance_reason": "Global events affect India through trade and capital flows.",
}

# Common alternative key names LLMs use instead of our schema
_KEY_ALIASES = {
    "event_title":            ["title", "event_name", "name", "headline"],
    "event_type":             ["type", "category", "event_category", "classification"],
    "scope":                  ["geographic_scope", "region", "geographic_region", "impact_scope"],
    "novelty":                ["novelty_type", "news_novelty", "information_type"],
    "speed":                  ["impact_speed", "timeframe", "timeline", "duration"],
    "us_relevance":           ["us_impact", "usa_relevance", "united_states_relevance"],
    "india_relevance":        ["india_impact", "india_significance"],
    "india_relevance_reason": ["india_reason", "india_context", "india_explanation"],
    "event_summary":          ["summary", "description", "overview"],
    "already_priced_in":      ["priced_in", "already_known"],
}


def _normalize(raw: dict) -> dict:
    """Resolve alternate key names and fill missing fields with fallback values."""
    # Unwrap if LLM nested everything under a single key
    if isinstance(raw, list) and raw:
        raw = raw[0]
    if isinstance(raw, dict) and len(raw) == 1:
        only_val = next(iter(raw.values()))
        if isinstance(only_val, dict):
            raw = only_val

    if not isinstance(raw, dict):
        return dict(_FALLBACK)

    result = dict(raw)  # copy

    for canonical, aliases in _KEY_ALIASES.items():
        if canonical not in result or not result[canonical]:
            for alias in aliases:
                if alias in raw and raw[alias]:
                    result[canonical] = raw[alias]
                    break

    # Fill any still-missing fields with fallback
    for key, default in _FALLBACK.items():
        if key not in result or result[key] is None:
            result[key] = default

    return result


def run_classifier(news_text: str) -> dict:
    llm = get_quick_llm()
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"Classify this news event:\n\n{news_text}"),
    ]
    response = llm.invoke(messages)
    raw = extract_json(response.content)
    result = _normalize(raw)
    if not result.get("event_summary"):
        result["event_summary"] = news_text[:300]
    return result
