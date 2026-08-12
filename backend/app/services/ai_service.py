"""Configurable LLM client — Gemini or OpenAI, selected via AI_PROVIDER.

This is the ONLY module that talks to an LLM provider directly. Every caller goes
through `generate_json()`, so swapping providers (or adding a third) never touches
calling code — see app/services/recommendation_service.py for the one current
consumer.

Deliberately narrow scope: this module knows how to get JSON out of an LLM and
nothing else. It has no opinion on resume content, scoring, or prompts — those live
in the services that call it.
"""
import json
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when the AI provider is unavailable, misconfigured, or returns
    something unusable. Callers should turn this into a friendly HTTP error —
    never leak the underlying exception (which may include request details) to
    the client."""


def _call_gemini(prompt: str, api_key: str, model: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    return response.text


def _call_openai(prompt: str, api_key: str, model: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


def generate_json(prompt: str) -> dict:
    """Send `prompt` to the configured provider and parse its response as JSON.

    Raises AIServiceError on any failure: missing API key, provider error, or a
    response that isn't valid JSON. Never raises the raw provider exception.
    """
    settings = get_settings()

    if not settings.ai_api_key:
        raise AIServiceError(
            "AI recommendations aren't configured yet — no API key is set on the server."
        )

    try:
        if settings.ai_provider == "openai":
            raw = _call_openai(prompt, settings.ai_api_key, settings.ai_model)
        else:
            raw = _call_gemini(prompt, settings.ai_api_key, settings.ai_model)
    except Exception as exc:
        logger.exception("AI provider (%s) call failed", settings.ai_provider)
        raise AIServiceError(
            "The AI service is temporarily unavailable. Please try again."
        ) from exc

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("AI provider returned non-JSON response: %r", (raw or "")[:500])
        raise AIServiceError(
            "The AI service returned an unexpected response. Please try again."
        ) from exc
