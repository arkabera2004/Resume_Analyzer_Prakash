"""Pydantic request/response schemas for resume-vs-job-description matching."""
from pydantic import BaseModel, Field

from app.schemas.job import JobDescriptionAnalysis
from app.schemas.resume import ParsedResume


class MatchAnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)


class MatchAnalyzeResponse(BaseModel):
    overall_match: int
    matching_skills: list[str]
    missing_skills: list[str]
    matching_keywords: list[str]
    missing_keywords: list[str]
    experience_relevance: int
    project_relevance: int
    explanation: list[str]
    parsed_resume: ParsedResume
    parsed_job: JobDescriptionAnalysis
