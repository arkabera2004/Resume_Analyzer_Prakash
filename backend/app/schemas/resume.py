"""Pydantic request/response schemas for resume upload."""
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    filename: str
    file_type: str  # "pdf" | "docx"
    character_count: int
    word_count: int
    extracted_text: str
