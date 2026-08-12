"""Pydantic request/response schemas for resume upload and parsing."""
from typing import Optional

from pydantic import BaseModel


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
