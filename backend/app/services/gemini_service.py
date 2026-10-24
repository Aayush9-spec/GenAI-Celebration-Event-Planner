"""
Gemini AI service — uses google-genai SDK (v1.x).
Handles plan generation, chat, and robust JSON parsing.
"""

import json
import logging
import re
from datetime import date
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.prompts import (
    BUDGET_CATEGORIES,
    CHAT_SYSTEM_PROMPT_TEMPLATE,
    FULL_PLAN_PROMPT_TEMPLATE,
    PLAN_SYSTEM_PROMPT,
    TIMELINE_GRANULARITY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


MODEL_NAME = "gemini-1.5-flash"

_GENERATE_CONFIG = types.GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=8192,
)


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def _safe_parse_json(raw: str) -> Dict[str, Any]:
    """Strip markdown fences and parse JSON. Falls back to regex extraction."""
    text = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text, flags=re.MULTILINE)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract outermost JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    raise ValueError(f"Could not parse JSON from Gemini response. Raw (first 400): {text[:400]}")


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_full_plan(event_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a complete event plan (budget, timeline, vendors, themes)
    as a structured JSON dict. Retries up to 3 times with backoff.
    """
    event_date = event_details.get("event_date")
    if isinstance(event_date, str):
        event_date_obj = date.fromisoformat(event_date)
    else:
        event_date_obj = event_date or date.today()

    days_until = (event_date_obj - date.today()).days
    event_type = event_details.get("event_type", "wedding")
    budget_cats = "\n".join(f"  - {c}" for c in BUDGET_CATEGORIES.get(event_type, []))

    prompt = FULL_PLAN_PROMPT_TEMPLATE.format(
        system_prompt=PLAN_SYSTEM_PROMPT,
        event_type=event_type,
        title=event_details.get("title", "My Event"),
        event_date=str(event_date),
        days_until=days_until,
        guest_count=event_details.get("guest_count", 100),
        total_budget=float(event_details.get("total_budget", 100000)),
        city=event_details.get("city") or "India",
        description=event_details.get("description") or "A special celebration",
        timeline_granularity=TIMELINE_GRANULARITY,
        budget_categories=budget_cats,
    )

    logger.info(f"Generating plan for: {event_details.get('title')}")
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=_GENERATE_CONFIG,
    )
    raw = response.text
    logger.debug(f"Gemini raw (first 500): {raw[:500]}")
    return _safe_parse_json(raw)


# ---------------------------------------------------------------------------
# Chat assistant
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def chat_with_assistant(
    event_details: Dict[str, Any],
    history: List[Dict[str, str]],
    user_message: str,
    latest_plan_summary: Optional[str] = None,
) -> str:
    """
    Send a chat message with full event context.
    history: list of {"role": "user"|"model", "parts": [text]}
    Returns the assistant's text response.
    """
    event_date = event_details.get("event_date", "")
    event_type = event_details.get("event_type", "event")

    plan_context = ""
    if latest_plan_summary:
        plan_context = f"\nLatest plan summary:\n{latest_plan_summary}"

    system_context = CHAT_SYSTEM_PROMPT_TEMPLATE.format(
        event_type=event_type,
        title=event_details.get("title", "My Event"),
        event_date=str(event_date),
        guest_count=event_details.get("guest_count", 100),
        total_budget=float(event_details.get("total_budget", 100000)),
        city=event_details.get("city") or "India",
        description=event_details.get("description") or "",
        plan_context=plan_context,
    )

    # Build Gemini content list (keep last 20 turns)
    # Format: alternating user/model messages
    contents = []
    trimmed_history = history[-20:]

    if not trimmed_history:
        # Inject system context as opening exchange
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=system_context + "\n\nHello! I need help planning my event.")],
            ),
            types.Content(
                role="model",
                parts=[types.Part(text="Hello! I'm your AI event planning assistant. I have all the details about your event and I'm ready to help. What would you like to plan first?")],
            ),
        ]
    else:
        # First message carries system context
        first = trimmed_history[0]
        contents.append(
            types.Content(
                role=first["role"],
                parts=[types.Part(text=system_context + "\n\n" + first["parts"][0])],
            )
        )
        for msg in trimmed_history[1:]:
            contents.append(
                types.Content(
                    role=msg["role"],
                    parts=[types.Part(text=msg["parts"][0])],
                )
            )

    contents.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=2048),
    )
    return response.text


# ---------------------------------------------------------------------------
# Budget-only generation
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_budget_breakdown(event_details: Dict[str, Any]) -> Dict[str, Any]:
    """Generate only the budget breakdown section (lightweight call)."""
    event_type = event_details.get("event_type", "wedding")
    budget_cats = "\n".join(f"  - {c}" for c in BUDGET_CATEGORIES.get(event_type, []))

    prompt = f"""{PLAN_SYSTEM_PROMPT}

Generate ONLY the budget_breakdown for:
- Event Type: {event_type}
- Guest Count: {event_details.get('guest_count', 100)}
- Total Budget: ₹{float(event_details.get('total_budget', 100000)):,.0f} INR
- City: {event_details.get('city') or 'India'}

Categories:
{budget_cats}

Return ONLY this JSON (no other keys, no markdown):
{{
  "budget_breakdown": {{
    "total": <number>,
    "currency": "INR",
    "items": [{{"category": "...", "amount": <number>, "percentage": <number>, "notes": "..."}}]
  }}
}}"""

    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=_GENERATE_CONFIG,
    )
    return _safe_parse_json(response.text)
