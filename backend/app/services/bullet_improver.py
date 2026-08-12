"""AI-powered improvement of a single resume bullet point.

Same grounding discipline as recommendation_service.py: the AI may rephrase,
tighten, and strengthen wording, but must never invent facts (metrics, companies,
technologies, scope) that weren't in the original bullet.
"""
from app.services.ai_service import AIServiceError, generate_json

MAX_BULLET_LENGTH = 500

_REQUIRED_KEYS = {"improved", "why_better"}


def _build_prompt(bullet_text: str, context: str | None) -> str:
    context_block = (
        f"\nSurrounding resume context (for grounding only — do not pull unrelated "
        f"facts from it into the bullet):\n---\n{context}\n---\n"
        if context
        else ""
    )

    return f"""You are a resume bullet-point editor. Improve exactly ONE bullet point.

STRICT RULES — violating any of these makes your response unusable:
- Never invent experience, skills, companies, technologies, or metrics that are not
  in the original bullet (or clearly implied by the surrounding context, if given).
  If the original has no numbers, do NOT add fabricated numbers — instead, suggest
  the *kind* of metric that would strengthen it in "why_better", not a made-up one.
- Preserve the factual scope of what the person actually did. Do not exaggerate
  impact, seniority, or scope beyond the original.
- Use a stronger, more specific action verb where appropriate.
- Add technical specificity ONLY using details already present in the bullet or
  context — never technologies/tools that aren't mentioned.
- Make it concise — remove filler words, avoid passive voice.

ORIGINAL BULLET:
---
{bullet_text}
---
{context_block}
Respond with ONLY a JSON object matching this exact shape:
{{
  "improved": <string — the rewritten bullet point>,
  "why_better": [<string>... 2-4 short reasons, e.g. "Stronger action verb", "More concise wording"]
}}"""


def _validate_response(data: object, original: str) -> dict:
    if not isinstance(data, dict) or not _REQUIRED_KEYS.issubset(data.keys()):
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")

    improved = data.get("improved")
    if not isinstance(improved, str) or not improved.strip():
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")

    why_better = [item for item in data.get("why_better", []) if isinstance(item, str)]

    return {
        "original": original,
        "improved": improved.strip(),
        "why_better": why_better,
    }


def improve_bullet(bullet_text: str, context: str | None = None) -> dict:
    """Call the configured LLM to improve a single resume bullet point.

    Raises AIServiceError (from ai_service or validation) on any failure.
    """
    prompt = _build_prompt(bullet_text, context)
    raw_response = generate_json(prompt)
    return _validate_response(raw_response, original=bullet_text)
