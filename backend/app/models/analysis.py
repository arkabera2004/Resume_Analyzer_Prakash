"""Analysis document model — mirrors the `analyses` MongoDB collection.

An "analysis" is one resume run (optionally against a job description), storing the
deterministic ATS score, job-match results, parsed resume data, and AI recommendations.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.py_object_id import PyObjectId


class SectionScore(BaseModel):
    score: int  # out of 10
    strengths: list[str] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AnalysisModel(BaseModel):
    """Shape of a document in the `analyses` collection."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId

    # Source metadata
    resume_name: str
    job_title: Optional[str] = None
    job_description: Optional[str] = None

    # Parsed resume data (see resume_parser service in a later phase)
    parsed_resume: dict[str, Any] = Field(default_factory=dict)

    # Deterministic ATS scoring (see ats_scorer service)
    ats_score: Optional[int] = None
    keyword_score: Optional[int] = None
    skills_score: Optional[int] = None
    structure_score: Optional[int] = None
    experience_score: Optional[int] = None
    project_score: Optional[int] = None
    formatting_score: Optional[int] = None

    # Job matching (see job_matcher service)
    match_score: Optional[int] = None
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matching_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    experience_relevance: Optional[int] = None
    project_relevance: Optional[int] = None

    # Section-by-section breakdown
    section_scores: dict[str, SectionScore] = Field(default_factory=dict)

    # AI-generated content (recommendation_service / ai_service)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    priority_improvements: list[str] = Field(default_factory=list)
    recommended_roles: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
