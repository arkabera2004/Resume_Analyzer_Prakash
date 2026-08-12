"""Pydantic request/response schemas for saving and browsing analyses."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.analysis import SectionScore


class SaveAnalysisRequest(BaseModel):
    """What the frontend sends after running ATS scoring / job matching / AI
    recommendations — this endpoint doesn't recompute anything, it just persists
    results the user already generated and chose to save."""

    resume_name: str = Field(min_length=1)
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    parsed_resume: dict[str, Any] = Field(default_factory=dict)

    ats_score: Optional[int] = None
    keyword_score: Optional[int] = None
    skills_score: Optional[int] = None
    structure_score: Optional[int] = None
    experience_score: Optional[int] = None
    project_score: Optional[int] = None
    formatting_score: Optional[int] = None

    match_score: Optional[int] = None
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matching_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    experience_relevance: Optional[int] = None
    project_relevance: Optional[int] = None

    section_scores: dict[str, SectionScore] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    priority_improvements: list[str] = Field(default_factory=list)
    recommended_roles: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AnalysisSummary(BaseModel):
    """Lightweight shape for history lists and dashboard 'recent analyses'."""

    id: str
    resume_name: str
    job_title: Optional[str] = None
    ats_score: Optional[int] = None
    match_score: Optional[int] = None
    created_at: datetime


class AnalysisDetail(AnalysisSummary):
    """Everything about one saved analysis."""

    parsed_resume: dict[str, Any]
    keyword_score: Optional[int] = None
    skills_score: Optional[int] = None
    structure_score: Optional[int] = None
    experience_score: Optional[int] = None
    project_score: Optional[int] = None
    formatting_score: Optional[int] = None
    matching_skills: list[str]
    missing_skills: list[str]
    matching_keywords: list[str]
    missing_keywords: list[str]
    experience_relevance: Optional[int] = None
    project_relevance: Optional[int] = None
    section_scores: dict[str, SectionScore]
    strengths: list[str]
    weaknesses: list[str]
    priority_improvements: list[str]
    recommended_roles: list[dict[str, Any]]
    recommendations: list[str]


class DashboardStats(BaseModel):
    total_analyses: int
    best_ats_score: Optional[int] = None
    avg_match_score: Optional[int] = None
    unique_skills_count: int
    recent_analyses: list[AnalysisSummary]


class CompareAnalysesRequest(BaseModel):
    analysis_id_a: str
    analysis_id_b: str


class CompareAnalysesResponse(BaseModel):
    """Compares two saved analyses. `analysis_a` is always the older of the two
    (by created_at) so 'improvement' consistently reads as a -> b, regardless of
    which id the caller passed first."""

    analysis_a: AnalysisSummary
    analysis_b: AnalysisSummary
    ats_score_change: Optional[int] = None
    match_score_change: Optional[int] = None
    new_skills: list[str]
    removed_skills: list[str]
    new_keywords: list[str]
    removed_keywords: list[str]
    improved_sections: list[str]
    regressed_sections: list[str]
