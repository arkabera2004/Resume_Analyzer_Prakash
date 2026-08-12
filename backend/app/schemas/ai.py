"""Pydantic request/response schemas for AI-generated resume recommendations."""
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
