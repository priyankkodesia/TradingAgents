"""LLM provider resolution for the newsagent package.

Priority: OpenAI (if OPENAI_API_KEY set) → Anthropic (if ANTHROPIC_API_KEY set).
Deep model  = best reasoning (Sonnet / GPT-4o).
Quick model = fast structured output (Haiku / GPT-4o-mini).
"""

import json
import os
import re
from functools import lru_cache


@lru_cache(maxsize=1)
def _provider() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    raise RuntimeError(
        "No LLM API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment."
    )


def get_deep_llm():
    """Best available reasoning model."""
    if _provider() == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            api_key=os.environ["OPENAI_API_KEY"],
            max_tokens=4096,
        )
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        max_tokens=4096,
    )


def get_quick_llm():
    """Fast model for structured / low-reasoning tasks."""
    if _provider() == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"],
            max_tokens=2048,
        )
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        max_tokens=2048,
    )


def active_provider() -> str:
    """Return 'openai' or 'anthropic' — whichever is active."""
    return _provider()


def check_llm_connection() -> str:
    """Verify API key is present and the connection works. Returns provider name.

    Raises RuntimeError on missing key or failed connectivity check.
    """
    provider = _provider()  # raises if no key

    try:
        llm = get_quick_llm()
        from langchain_core.messages import HumanMessage
        llm.invoke([HumanMessage(content="Reply with the single word: OK")])
    except Exception as exc:
        msg = str(exc)
        if any(k in msg.lower() for k in ("auth", "invalid", "incorrect", "unauthorized", "401", "403", "api key")):
            raise RuntimeError(
                f"{provider.capitalize()} API key is invalid or rejected. "
                f"Check your {'OPENAI_API_KEY' if provider == 'openai' else 'ANTHROPIC_API_KEY'} value. "
                f"Detail: {msg}"
            ) from exc
        raise RuntimeError(
            f"LLM connectivity check failed ({provider}): {msg}"
        ) from exc

    return provider


def extract_json(text: str) -> dict | list:
    """Parse JSON from LLM output, tolerating markdown code fences."""
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for pattern in (r"\{[\s\S]+\}", r"\[[\s\S]+\]"):
            m = re.search(pattern, text)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
    return {}
