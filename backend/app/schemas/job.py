"""Pydantic request/response schemas for job description analysis."""
from typing import Optional

from pydantic import BaseModel, Field


# Generous upper bound for a pasted job posting — bounds payload size reaching
# regex/AI processing downstream.
MAX_JOB_DESCRIPTION_LENGTH = 20_000


class JobAnalyzeRequest(BaseModel):
    job_description: str = Field(min_length=1, max_length=MAX_JOB_DESCRIPTION_LENGTH)


class JobDescriptionAnalysis(BaseModel):
    job_title: Optional[str] = None
    required_skills: list[str]
    preferred_skills: list[str]
    technologies: list[str]
    keywords: list[str]
    experience_requirements: list[str]
    education_requirements: list[str]
    responsibilities: list[str]
