"""Pydantic request/response schemas for resume upload and parsing."""
from typing import Optional

from pydantic import BaseModel, Field

# Generous upper bound for pasted/extracted resume text — far beyond any real
# resume, but bounds the payload size reaching regex/AI processing downstream.
MAX_RESUME_TEXT_LENGTH = 50_000


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class ParsedResume(BaseModel):
    contact: ContactInfo
    skills: dict[str, list[str]]
    education: list[str]
    experience: list[str]
    internships: list[str]
    projects: list[str]
    certifications: list[str]
    achievements: list[str]
    summary: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    filename: str
    file_type: str  # "pdf" | "docx"
    character_count: int
    word_count: int
    extracted_text: str
    parsed: ParsedResume


class ATSScoreRequest(BaseModel):
    """Re-analyze already-extracted text (from a prior /upload call) — avoids
    re-uploading the file just to compute a score."""
    extracted_text: str = Field(min_length=1, max_length=MAX_RESUME_TEXT_LENGTH)


class ATSScoreResponse(BaseModel):
    overall_score: int
    keyword_score: int
    skills_score: int
    structure_score: int
    experience_score: int
    project_score: int
    formatting_score: int
    parsed: ParsedResume
