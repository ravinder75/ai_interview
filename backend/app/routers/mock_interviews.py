import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import InterviewSession, InterviewQuestion, CandidateAnswer, User, Resume, InterviewMessage
from app.security import get_current_user

Base.metadata.create_all(bind=engine)
from app.services.ai_service import ai_service
from app.services.assessment_engine import assessment_engine
from app.services.feedback_service import feedback_service
from app.schemas.interview import SessionDetailResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mock-interviews", tags=["MockInterviews"])

class StartMockRequest(BaseModel):
    role: str = Field("Software Engineer")
    experience_level: str = Field("Mid-Level")
    interview_type: str = Field("technical")
    interview_style: str = Field("friendly")
    difficulty: str = Field("medium")
    duration_minutes: int = Field(30)
    resume_id: Optional[str] = None
    candidate_profile: Optional[Dict[str, Any]] = None

class SubmitAnswerRequest(BaseModel):
    question: str
    answer: str
    question_type: Optional[str] = "technical"
    difficulty: Optional[str] = "medium"

class NextQuestionRequest(BaseModel):
    current_question: Optional[str] = None
    last_answer: Optional[str] = None
    previous_questions: Optional[List[str]] = []

@router.post("/start")
async def start_mock_interview(
    req: StartMockRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    Base.metadata.create_all(bind=engine)
    session_id = f"sess-{uuid.uuid4().hex[:12]}"
    user_id = current_user.id if current_user else None

    # Load candidate resume associated ONLY with authenticated user
    resume_obj = None
    if req.resume_id:
        query = db.query(Resume).filter(Resume.resume_id == req.resume_id)
        if current_user:
            query = query.filter(Resume.user_id == current_user.id)
        resume_obj = query.first()

    if not resume_obj and current_user:
        resume_obj = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).first()

    profile_dict = req.candidate_profile or {}
    if resume_obj:
        p_info = resume_obj.personal_info or {}
        profile_dict = {
            "name": p_info.get("name") or (current_user.full_name if current_user else "Candidate"),
            "target_role": req.role,
            "experience_level": req.experience_level,
            "skills": resume_obj.skills or profile_dict.get("skills") or [],
            "projects": resume_obj.projects or profile_dict.get("projects") or [],
            "experience": resume_obj.experience or profile_dict.get("experience") or [],
            "extracted_text": (resume_obj.extracted_text or "")[:1500]
        }
    else:
        profile_dict = {
            "name": current_user.full_name if current_user else "Candidate",
            "target_role": req.role,
            "experience_level": req.experience_level,
            "skills": profile_dict.get("skills") or ["Technical Fundamentals", "Problem Solving"],
            "projects": profile_dict.get("projects") or [{"name": "Primary Project"}]
        }

    # Generate personalized first question
    first_q_data = await generate_structured_question(
        role=req.role,
        experience=req.experience_level,
        difficulty=req.difficulty,
        profile=profile_dict,
        previous_questions=[]
    )

    db_session = InterviewSession(
        session_id=session_id,
        user_id=user_id,
        title=f"{req.role} AI Mock Interview",
        mode="mock",
        role=req.role,
        experience_level=req.experience_level,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        resume_id=resume_obj.resume_id if resume_obj else None,
        candidate_profile=profile_dict,
        duration_minutes=req.duration_minutes,
        overall_score=0.0,
        status="active"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Save initial assistant question message
    msg = InterviewMessage(
        session_id=session_id,
        role="assistant",
        content=first_q_data["question"],
        category=first_q_data["question_type"]
    )
    db.add(msg)
    db.commit()

    return {
        "session_id": session_id,
        "role": req.role,
        "status": "active",
        "candidate_profile": profile_dict,
        "first_question": first_q_data
    }

@router.post("/{session_id}/answer")
async def save_candidate_answer(
    session_id: str,
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()

    # Create session if it doesn't exist (client-side-only session IDs)
    if not session:
        user_id = current_user.id if current_user else None
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            title="AI Mock Interview",
            mode="mock",
            role="Software Engineer",
            status="active",
            overall_score=0.0
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    if current_user and session.user_id and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to session")

    msg = InterviewMessage(
        session_id=session_id,
        role="user",
        content=req.answer.strip(),
        category=req.question_type or "technical"
    )
    db.add(msg)
    db.commit()

    return {"status": "saved", "session_id": session_id, "message_id": msg.id}

@router.post("/{session_id}/evaluate")
async def evaluate_answer(
    session_id: str,
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()

    eval_result = await assessment_engine.evaluate_single_answer(
        question=req.question,
        answer=req.answer,
        category=req.question_type or "technical",
        difficulty=req.difficulty or (session.difficulty if session else "medium"),
        job_title=session.role if session else "Software Engineer"
    )

    structured_eval = {
        "score": eval_result.get("overall_score", 80),
        "technical_accuracy": eval_result.get("technical_accuracy", 80),
        "relevance": eval_result.get("relevance", 85),
        "communication": eval_result.get("communication", 85),
        "completeness": eval_result.get("completeness", 80),
        "strengths": eval_result.get("strengths", []),
        "improvements": eval_result.get("weaknesses", []),
        "missing_points": eval_result.get("missing_concepts", []),
        "ideal_answer_summary": f"Cover direct technical definition, trade-offs, and practical project implementation metrics for '{req.question}'."
    }

    return structured_eval

@router.post("/{session_id}/next-question")
async def get_next_question(
    session_id: str,
    req: NextQuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()

    role = session.role if session else "Software Engineer"
    experience = session.experience_level if session else "Mid-Level"
    difficulty = session.difficulty if session else "medium"
    profile = session.candidate_profile if session else {}

    prev_qs = req.previous_questions or []
    if req.current_question and req.current_question not in prev_qs:
        prev_qs.append(req.current_question)

    q_data = await generate_structured_question(
        role=role,
        experience=experience,
        difficulty=difficulty,
        profile=profile,
        previous_questions=prev_qs,
        last_answer=req.last_answer
    )

    msg = InterviewMessage(
        session_id=session_id,
        role="assistant",
        content=q_data["question"],
        category=q_data["question_type"]
    )
    db.add(msg)
    db.commit()

    return q_data

@router.post("/{session_id}/finish")
@router.post("/{session_id}/end")
async def finish_mock_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    Base.metadata.create_all(bind=engine)
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()

    # Create session if it doesn't exist (client-side-only sessions)
    if not session:
        user_id = current_user.id if current_user else None
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            title="AI Mock Interview",
            mode="mock",
            role="Software Engineer",
            experience_level="Mid-Level",
            interview_type="technical",
            difficulty="medium",
            duration_minutes=30,
            overall_score=0.0,
            status="completed",
            ended_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        db.commit()

    # Trigger complete report generation pipeline
    try:
        from app.routers.interviews import generate_interview_report
        report = await generate_interview_report(session_id=session_id, db=db, current_user=current_user)
    except Exception as e:
        logger.warning(f"Report generation failed for {session_id}: {e}")
        report = {
            "overall_score": 75,
            "summary": "Interview session completed. Detailed evaluation pending.",
            "session_id": session_id,
            "status": "completed"
        }

    return {
        "status": "completed",
        "session_id": session_id,
        "report": report
    }

@router.get("/{session_id}")
def get_mock_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found")
    return session

@router.get("/{session_id}/report")
async def get_mock_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    from app.routers.interviews import get_interview_report
    return await get_interview_report(session_id=session_id, db=db, current_user=current_user)

async def generate_structured_question(
    role: str,
    experience: str,
    difficulty: str,
    profile: Dict[str, Any],
    previous_questions: List[str],
    last_answer: Optional[str] = None
) -> Dict[str, Any]:
    cand_name = profile.get("name", "Candidate")
    projects = profile.get("projects", [])
    skills = profile.get("skills", [])

    proj_name = "Primary Project"
    if projects and len(projects) > 0:
        proj_name = projects[0].get("name") if isinstance(projects[0], dict) else str(projects[0])

    skill_str = ", ".join(skills[:4]) if skills else "System Architecture, Problem Solving"

    sys_prompt = f"""You are a Senior Technical Interviewer conducting a mock interview for the role of {role}.
Generate ONE targeted, non-duplicate interview question tailored to the candidate's background.

Candidate: {cand_name}
Target Role: {role}
Experience: {experience}
Key Skills: {skill_str}
Key Project: {proj_name}

Rules:
1. Do NOT ask any of these previously asked questions: {previous_questions}
2. Make questions role-specific, realistic, and highly relevant.
3. Return ONLY valid JSON matching this schema:
{{
  "question": "Your single specific interview question text here.",
  "question_type": "technical|behavioral|scenario|project|coding",
  "difficulty": "{difficulty}",
  "topic": "Specific technical area or skill",
  "expected_points": ["Point 1", "Point 2", "Point 3"]
}}"""

    user_prompt = "Generate the next structured interview question."
    if last_answer:
        user_prompt += f" Previous answer given by candidate: '{last_answer[:300]}'."

    try:
        res = await ai_service.generate_json(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        if isinstance(res, dict) and "question" in res:
            q_text = res["question"].strip()
            if q_text in previous_questions:
                res["question"] += " Could you walk through a concrete scenario from your experience?"
            return res
    except Exception as e:
        logger.warn(f"Failed to generate JSON question from AI: {e}")

    q_index = len(previous_questions) + 1
    fallback_qs = [
        f"Walk me through your key technical contributions in {proj_name} for the {role} position.",
        f"How do you approach debugging and performance optimization when working with {skill_str}?",
        f"Can you describe a challenging technical trade-off you had to make in a recent project?",
        f"In a high-throughput environment, how do you design components to ensure scalability and reliability?",
        f"Tell me about a time when a system design or implementation did not go as planned, and how you recovered."
    ]
    selected_q = fallback_qs[(q_index - 1) % len(fallback_qs)]

    return {
        "question": selected_q,
        "question_type": "technical" if q_index % 2 == 1 else "scenario",
        "difficulty": difficulty,
        "topic": role,
        "expected_points": ["Direct explanation", "Architecture & design", "Measurable outcome"]
    }
