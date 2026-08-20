from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview_bit import CandidateProfile
from app.models.resume import Resume
from app.security import get_current_user
from app.prompts.interview_bit import get_interview_bit_prompt
from app.schemas.ai import (
    AnswerEvaluationRequest, AnswerEvaluationResponse,
    ResumeAnswerRequest, ResumeAnswerResponse,
    ChatRequest, ChatResponse
)
from app.services.feedback_service import feedback_service
from app.services.ai_service import ai_service
from app.services.profile_normalizer import get_normalized_candidate_context

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])

@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_answer(request: AnswerEvaluationRequest):
    evaluation = await feedback_service.evaluate_answer(
        question=request.question,
        answer=request.answer,
        job_title=request.job_title or "Software Engineer",
        job_description=request.job_description or ""
    )
    return evaluation

@router.post("/resume-answer", response_model=ResumeAnswerResponse)
async def generate_resume_answer(request: ResumeAnswerRequest):
    messages = [
        {"role": "system", "content": "You are an expert interview coach. Based on the candidate's uploaded resume/bio details and the target role, craft a tailored high-scoring STAR framework practice response for the interview question. Return JSON matching: {\"generated_answer\": \"...\", \"key_talking_points\": [\"...\"]}"},
        {"role": "user", "content": f"Role: {request.role}\nQuestion: {request.question}\nResume/Bio Context: {request.resume_text}"}
    ]
    try:
        res = await ai_service.generate_json(
            messages=messages
        )
        return ResumeAnswerResponse(
            generated_answer=res.get("generated_answer", "Based on your resume experience, start by outlining your technical leadership, specific tools used, and key business outcomes."),
            key_talking_points=res.get("key_talking_points", ["Highlight core technologies", "Quantify business results", "Mention team leadership"])
        )
    except Exception:
        return ResumeAnswerResponse(
            generated_answer=f"As a {request.role}, I leverage my background in software architecture and cloud infrastructure to deliver high-availability systems. In my recent work outlined in my resume, I led key engineering initiatives that optimized backend latency and streamlined deployment pipelines.",
            key_talking_points=["Core technical skills", "System optimization", "Leadership & impact"]
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    profile_dict = get_normalized_candidate_context(db, current_user)
    system_prompt = get_interview_bit_prompt(profile_dict)
    system_msg = {"role": "system", "content": system_prompt}

    user_msgs = [m.model_dump() for m in request.messages]
    msgs = [system_msg] + user_msgs

    try:
        reply = await ai_service.generate_text(
            messages=msgs,
            temperature=request.temperature or 0.7
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        last_question = user_msgs[-1]["content"] if user_msgs else "your question"
        return ChatResponse(
            reply=f"I'm here to help answer '{last_question}' based on your candidate profile."
        )

