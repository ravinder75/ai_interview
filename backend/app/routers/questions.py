from typing import List
from fastapi import APIRouter, Depends
from app.schemas.interview import QuestionGenerateRequest, QuestionResponse
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/questions", tags=["Questions"])

@router.post("/generate", response_model=List[QuestionResponse])
async def generate_questions(request: QuestionGenerateRequest):
    questions = await interview_service.generate_questions(
        role=request.role,
        experience=request.experience,
        industry=request.industry,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        count=request.count
    )
    return questions
