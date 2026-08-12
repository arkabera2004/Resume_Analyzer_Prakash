"""AI-generated resume recommendations: section-by-section scoring, strengths/
weaknesses, priority improvements, and job role suggestions.

Unlike ats_scorer.py and job_matcher.py, this service DOES call an LLM — this is
where nuanced natural-language judgment genuinely earns its keep. But the prompt
below is deliberately strict about staying grounded in what's actually in the
resume: the AI is told what sections were detected and forbidden from inventing
anything not present in the source text.
"""
from app.services.ai_service import AIServiceError, generate_json

SECTION_KEYS = [
    "summary", "education", "skills", "experience", "projects",
    "certifications", "achievements",
]

_REQUIRED_TOP_LEVEL_KEYS = {
    "section_scores", "strengths", "weaknesses", "priority_improvements", "recommended_roles",
}


def _build_prompt(resume_text: str, parsed_resume: dict) -> str:
    detected_skills = [skill for skills in parsed_resume["skills"].values() for skill in skills]

    return f"""You are a resume-review assistant. Analyze ONLY the resume text below.

STRICT RULES — violating any of these makes your response unusable:
- Never invent candidate information: no skills, companies, job titles, metrics, or
  achievements that are not literally present in the resume text.
- If a section is missing or empty, say so plainly (e.g. "No certifications listed")
  instead of inventing content to fill it.
- Job role recommendations must be grounded in the skills actually detected below —
  do not recommend roles unrelated to the candidate's demonstrated skills, and do not
  make unsupported claims about fit.
- Base match_percentage for each recommended role on how well the detected skills
  align with that role's typical requirements — use your judgment, but keep it
  defensible and vary it meaningfully across roles (don't just say 90% for everything).

Detected skills (already extracted deterministically, for your reference):
{", ".join(detected_skills) if detected_skills else "(none detected)"}

RESUME TEXT:
---
{resume_text}
---

Respond with ONLY a JSON object matching this exact shape:
{{
  "section_scores": {{
    "summary": {{"score": <0-10 int>, "strengths": [<string>...], "problems": [<string>...], "recommendations": [<string>...]}},
    "education": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}},
    "skills": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}},
    "experience": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}},
    "projects": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}},
    "certifications": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}},
    "achievements": {{"score": <0-10 int>, "strengths": [...], "problems": [...], "recommendations": [...]}}
  }},
  "strengths": [<string>...],
  "weaknesses": [<string>...],
  "priority_improvements": [<string>... ordered most important first, 3-5 items],
  "recommended_roles": [
    {{"role": <string>, "match_percentage": <0-100 int>, "reason": <string>}}
    ... 3-5 roles, ordered highest match first
  ]
}}"""


def _validate_section_score(value: object) -> dict:
    if not isinstance(value, dict):
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")
    score = value.get("score")
    if not isinstance(score, (int, float)):
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")
    return {
        "score": max(0, min(10, int(score))),
        "strengths": [str(item) for item in value.get("strengths", []) if isinstance(item, str)],
        "problems": [str(item) for item in value.get("problems", []) if isinstance(item, str)],
        "recommendations": [
            str(item) for item in value.get("recommendations", []) if isinstance(item, str)
        ],
    }


def _validate_response(data: object) -> dict:
    """Defensive parsing: an LLM response is untrusted input, even when it's
    supposed to be JSON. Malformed shapes are turned into a clear error rather
    than silently propagating bad/missing data to the client."""
    if not isinstance(data, dict) or not _REQUIRED_TOP_LEVEL_KEYS.issubset(data.keys()):
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")

    raw_sections = data.get("section_scores")
    if not isinstance(raw_sections, dict):
        raise AIServiceError("The AI service returned an unexpected response. Please try again.")

    section_scores = {}
    for key in SECTION_KEYS:
        if key in raw_sections:
            section_scores[key] = _validate_section_score(raw_sections[key])

    recommended_roles = []
    for role in data.get("recommended_roles", []):
        if not isinstance(role, dict):
            continue
        name = role.get("role")
        percentage = role.get("match_percentage")
        if isinstance(name, str) and isinstance(percentage, (int, float)):
            recommended_roles.append({
                "role": name,
                "match_percentage": max(0, min(100, int(percentage))),
                "reason": str(role.get("reason", "")),
            })

    return {
        "section_scores": section_scores,
        "strengths": [s for s in data.get("strengths", []) if isinstance(s, str)],
        "weaknesses": [s for s in data.get("weaknesses", []) if isinstance(s, str)],
        "priority_improvements": [
            s for s in data.get("priority_improvements", []) if isinstance(s, str)
        ],
        "recommended_roles": recommended_roles,
    }


def get_ai_recommendations(resume_text: str, parsed_resume: dict) -> dict:
    """Call the configured LLM and return validated section scores, strengths/
    weaknesses, priority improvements, and job role recommendations.

    Raises AIServiceError (from ai_service or validation) on any failure — callers
    should turn this into a 502/503, never a raw 500 with a stack trace.
    """
    prompt = _build_prompt(resume_text, parsed_resume)
    raw_response = generate_json(prompt)
    return _validate_response(raw_response)
