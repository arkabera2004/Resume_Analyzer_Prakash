"""Resume upload, parsing, and ATS scoring routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.config import get_settings
from app.models.user import UserModel
from app.schemas.resume import ATSScoreRequest, ATSScoreResponse, ResumeUploadResponse
from app.services.ats_scorer import score_resume
from app.services.resume_parser import ResumeParsingError, extract_resume_text, get_file_extension
from app.services.resume_structurer import structure_resume
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/resume", tags=["resume"])

settings = get_settings()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile,
    _current_user: UserModel = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided.")

    content = await file.read()

    try:
        text = extract_resume_text(
            filename=file.filename,
            content_type=file.content_type,
            content=content,
            max_size_mb=settings.max_upload_size_mb,
        )
    except ResumeParsingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return ResumeUploadResponse(
        filename=file.filename,
        file_type=get_file_extension(file.filename),
        character_count=len(text),
        word_count=len(text.split()),
        extracted_text=text,
        parsed=structure_resume(text),
    )


@router.post("/analyze", response_model=ATSScoreResponse)
async def analyze_resume(
    payload: ATSScoreRequest,
    _current_user: UserModel = Depends(get_current_user),
):
    """Compute the deterministic ATS score for already-extracted resume text."""
    text = payload.extracted_text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resume text provided.")

    parsed = structure_resume(text)
    scores = score_resume(text, parsed)

    return ATSScoreResponse(**scores, parsed=parsed)
