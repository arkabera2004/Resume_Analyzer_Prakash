"""Pydantic request/response schemas for job description analysis."""
from typing import Optional

from pydantic import BaseModel, Field


class JobAnalyzeRequest(BaseModel):
    job_description: str = Field(min_length=1)


class JobDescriptionAnalysis(BaseModel):
    job_title: Optional[str] = None
    required_skills: list[str]
    preferred_skills: list[str]
    technologies: list[str]
    keywords: list[str]
    experience_requirements: list[str]
    education_requirements: list[str]
    responsibilities: list[str]
