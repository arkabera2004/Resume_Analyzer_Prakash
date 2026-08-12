"""Pydantic request/response schemas for AI-generated resume recommendations."""
from typing import Optional

from pydantic import BaseModel, Field


class AIRecommendationsRequest(BaseModel):
    resume_text: str = Field(min_length=1)


class SectionScore(BaseModel):
    score: int
    strengths: list[str]
    problems: list[str]
    recommendations: list[str]


class RecommendedRole(BaseModel):
    role: str
    match_percentage: int
    reason: str


class AIRecommendationsResponse(BaseModel):
    section_scores: dict[str, SectionScore]
    strengths: list[str]
    weaknesses: list[str]
    priority_improvements: list[str]
    recommended_roles: list[RecommendedRole]


class ImproveBulletRequest(BaseModel):
    bullet_text: str = Field(min_length=1, max_length=500)
    # Optional surrounding resume text, purely for grounding (e.g. so "built the
    # backend" can be improved with the tech stack already mentioned elsewhere) —
    # never a license to pull in unrelated facts.
    context: Optional[str] = Field(default=None, max_length=4000)


class ImproveBulletResponse(BaseModel):
    original: str
    improved: str
    why_better: list[str]
