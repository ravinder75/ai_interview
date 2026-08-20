import re
import uuid
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion, CandidateAnswer, Feedback, InterviewMessage, InterviewNotification
from app.models.interview_bit import InterviewBitMessage
from app.schemas.interview import (
    StartSessionRequest, SessionDetailResponse, AnswerSubmissionRequest,
    FeedbackResponse, AskQuestionRequest, MessageResponse,
    ScheduleInterviewRequest, ScheduledInterviewResponse, InterviewResultResponse
)
from app.security import get_current_user
from app.services.interview_service import interview_service
from app.services.feedback_service import feedback_service
from app.services.ai_service import ai_service
from app.prompts.interview_bit import get_interview_bit_prompt
from app.prompts.mock_interviewer import get_mock_interviewer_prompt
from app.services.profile_normalizer import get_normalized_candidate_context
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interviews", tags=["Interviews"])
Base.metadata.create_all(bind=engine)

class UpdateSessionRequest(BaseModel):
    role: Optional[str] = None
    interview_type: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    scheduled_at: Optional[datetime] = None

def parse_utc_scheduled_at(req: ScheduleInterviewRequest) -> datetime:
    if req.scheduled_at:
        if isinstance(req.scheduled_at, datetime):
            dt = req.scheduled_at
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
        elif isinstance(req.scheduled_at, str):
            try:
                dt = datetime.fromisoformat(req.scheduled_at.replace("Z", "+00:00"))
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
            except Exception:
                pass

    if req.scheduled_date and req.scheduled_time:
        try:
            time_str = req.scheduled_time.strip()
            if len(time_str.split(":")) == 2:
                time_str += ":00"
            combined_str = f"{req.scheduled_date}T{time_str}"
            dt = datetime.fromisoformat(combined_str)
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
        except Exception as e:
            logger.warning(f"Could not parse scheduled date/time string ({req.scheduled_date}, {req.scheduled_time}): {e}")

    return datetime.now(timezone.utc) + timedelta(minutes=30)

def evaluate_session_status(session: InterviewSession, now_utc: datetime) -> str:
    current_st = (session.status or "SCHEDULED").upper()
    if current_st in ["IN_PROGRESS", "COMPLETED", "EXITED"]:
        return current_st

    if not session.scheduled_at:
        return current_st

    sched_utc = session.scheduled_at
    if sched_utc.tzinfo is None:
        sched_utc = sched_utc.replace(tzinfo=timezone.utc)
    else:
        sched_utc = sched_utc.astimezone(timezone.utc)

    grace_expiry_utc = sched_utc + timedelta(minutes=10)

    if now_utc < sched_utc:
        return "SCHEDULED"
    elif sched_utc <= now_utc <= grace_expiry_utc:
        return "READY"
    else:
        return "MISSED"

def resolve_active_user(db: Session, current_user: Optional[User]) -> User:
    if current_user:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please sign in to create and start an interview.",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/schedule")
def schedule_interview(
    req: ScheduleInterviewRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)

    Base.metadata.create_all(bind=engine)
    session_uuid = f"sched-{uuid.uuid4()}"
    role_str = req.role or "Software Engineer"
    type_str = req.interview_type or req.type or "technical"
    title = f"{role_str} ({type_str.replace('_', ' ').title()})"
    
    parsed_scheduled_at = parse_utc_scheduled_at(req)
    now_utc = datetime.now(timezone.utc)

    # Reject past scheduled date + time
    if parsed_scheduled_at <= now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a future interview time."
        )

    # Check for duplicate schedules created within 10 seconds for the same user and role
    recent_duplicate = db.query(InterviewSession).filter(
        InterviewSession.user_id == active_user.id,
        InterviewSession.role == role_str,
        InterviewSession.status.in_(["SCHEDULED", "READY"]),
        InterviewSession.created_at >= datetime.now(timezone.utc) - timedelta(seconds=10)
    ).first()

    if recent_duplicate:
        return {
            "id": recent_duplicate.session_id,
            "session_id": recent_duplicate.session_id,
            "status": recent_duplicate.status,
            "role": recent_duplicate.role,
            "interview_type": recent_duplicate.interview_type,
            "difficulty": recent_duplicate.difficulty,
            "scheduled_at": recent_duplicate.scheduled_at,
            "duration_minutes": recent_duplicate.duration_minutes,
            "timezone": recent_duplicate.timezone or "UTC",
            "resume_id": recent_duplicate.resume_id,
            "created_at": recent_duplicate.created_at
        }

    db_session = InterviewSession(
        session_id=session_uuid,
        user_id=active_user.id,
        title=title,
        mode="scheduled_mock",
        role=role_str,
        experience_level="Mid-Level",
        industry="Technology",
        interview_type=type_str,
        difficulty=req.difficulty or "medium",
        scheduled_at=parsed_scheduled_at,
        duration_minutes=req.duration_minutes or 30,
        programming_language=req.programming_language or "Python",
        timezone=req.timezone or "UTC",
        resume_id=req.resume_id,
        status="SCHEDULED"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return {
        "id": db_session.session_id,
        "session_id": db_session.session_id,
        "status": db_session.status,
        "role": db_session.role,
        "interview_type": db_session.interview_type,
        "difficulty": db_session.difficulty,
        "scheduled_at": db_session.scheduled_at,
        "duration_minutes": db_session.duration_minutes,
        "timezone": db_session.timezone,
        "resume_id": db_session.resume_id,
        "created_at": db_session.created_at
    }

@router.get("/scheduled")
def get_scheduled_interviews(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)

    now_utc = datetime.now(timezone.utc)
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == active_user.id
    ).order_by(InterviewSession.created_at.desc()).all()

    result = []
    need_commit = False

    for s in sessions:
        if not s.scheduled_at:
            continue

        sched_utc = s.scheduled_at
        if sched_utc.tzinfo is None:
            sched_utc = sched_utc.replace(tzinfo=timezone.utc)
        else:
            sched_utc = sched_utc.astimezone(timezone.utc)

        grace_expiry_utc = sched_utc + timedelta(minutes=10)
        live_status = evaluate_session_status(s, now_utc)

        if s.status != live_status and s.status not in ["IN_PROGRESS", "COMPLETED", "EXITED"]:
            s.status = live_status
            need_commit = True

        starts_in_sec = max(0, int((sched_utc - now_utc).total_seconds()))
        remaining_grace_sec = max(0, int((grace_expiry_utc - now_utc).total_seconds()))

        result.append({
            "id": s.id,
            "session_id": s.session_id,
            "user_id": s.user_id,
            "role": s.role or "Software Engineer",
            "interview_type": s.interview_type or "technical",
            "difficulty": s.difficulty or "medium",
            "duration_minutes": s.duration_minutes or 30,
            "scheduled_at": sched_utc.isoformat(),
            "timezone": s.timezone or "UTC",
            "resume_id": s.resume_id,
            "status": live_status,
            "starts_in_seconds": starts_in_sec,
            "remaining_grace_seconds": remaining_grace_sec,
            "created_at": s.created_at.isoformat() if s.created_at else None
        })

    if need_commit:
        db.commit()

    return result

@router.post("/{interview_id}/start")
def start_scheduled_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)

    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == interview_id) | (InterviewSession.id == interview_id)
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Scheduled interview not found")

    # Strict User Isolation Check
    if session.user_id and session.user_id != active_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this interview schedule")

    if not session.user_id:
        session.user_id = active_user.id

    now_utc = datetime.now(timezone.utc)
    if session.scheduled_at:
        sched_utc = session.scheduled_at
        if sched_utc.tzinfo is None:
            sched_utc = sched_utc.replace(tzinfo=timezone.utc)
        else:
            sched_utc = sched_utc.astimezone(timezone.utc)

        grace_expiry_utc = sched_utc + timedelta(minutes=10)

        # 1. Reject if earlier than scheduled start time
        if now_utc < sched_utc:
            remaining_secs = int((sched_utc - now_utc).total_seconds())
            mins, secs = divmod(remaining_secs, 60)
            raise HTTPException(
                status_code=400,
                detail=f"Interview has not started yet. Starts in {mins:02d}:{secs:02d}."
            )

        # 2. Reject and mark MISSED if past 10-minute grace period
        if now_utc > grace_expiry_utc:
            session.status = "MISSED"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Interview join window has expired (10-minute grace period passed). Marked as MISSED."
            )

    if session.status in ["COMPLETED", "MISSED", "EXITED"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start interview with status '{session.status}'."
        )

    session.status = "IN_PROGRESS"
    session.started_at = now_utc
    db.commit()
    db.refresh(session)

    return {
        "status": "IN_PROGRESS",
        "session_id": session.session_id,
        "role": session.role,
        "interview_type": session.interview_type,
        "resume_id": session.resume_id,
        "started_at": session.started_at.isoformat() if session.started_at else None
    }

@router.post("/{interview_id}/miss")
def mark_interview_missed(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)

    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == interview_id) | (InterviewSession.id == interview_id)
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview schedule not found")

    if session.user_id and session.user_id != active_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to interview schedule")

    session.status = "MISSED"
    db.commit()
    return {"status": "MISSED", "session_id": session.session_id}

@router.get("/notifications")
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)
    if not active_user:
        return []

    now_utc = datetime.now(timezone.utc)
    user_sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == active_user.id,
        InterviewSession.scheduled_at.isnot(None)
    ).all()

    for s in user_sessions:
        sched_utc = s.scheduled_at
        if sched_utc.tzinfo is None:
            sched_utc = sched_utc.replace(tzinfo=timezone.utc)
        else:
            sched_utc = sched_utc.astimezone(timezone.utc)

        grace_expiry_utc = sched_utc + timedelta(minutes=10)
        warning_5m_utc = sched_utc + timedelta(minutes=5)
        reminder_30m_utc = sched_utc - timedelta(minutes=30)

        # 30-minute reminder
        if reminder_30m_utc <= now_utc < sched_utc:
            existing = db.query(InterviewNotification).filter(
                InterviewNotification.user_id == active_user.id,
                InterviewNotification.session_id == s.session_id,
                InterviewNotification.notification_type == "REMINDER_30M"
            ).first()
            if not existing:
                db.add(InterviewNotification(
                    user_id=active_user.id,
                    session_id=s.session_id,
                    notification_type="REMINDER_30M",
                    title="Interview Starting Soon",
                    message=f"Your {s.role} interview starts in 30 minutes.",
                    data={
                        "role": s.role,
                        "type": s.interview_type,
                        "session_id": s.session_id,
                        "scheduled_at": sched_utc.isoformat()
                    }
                ))

        # At scheduled time (READY)
        if sched_utc <= now_utc <= grace_expiry_utc:
            existing = db.query(InterviewNotification).filter(
                InterviewNotification.user_id == active_user.id,
                InterviewNotification.session_id == s.session_id,
                InterviewNotification.notification_type == "READY_START"
            ).first()
            if not existing:
                db.add(InterviewNotification(
                    user_id=active_user.id,
                    session_id=s.session_id,
                    notification_type="READY_START",
                    title="Interview Ready To Start",
                    message=f"Your {s.role} interview is ready to start.",
                    data={
                        "role": s.role,
                        "type": s.interview_type,
                        "session_id": s.session_id,
                        "scheduled_at": sched_utc.isoformat()
                    }
                ))

        # 5 minutes before grace-period expiration
        if warning_5m_utc <= now_utc <= grace_expiry_utc:
            existing = db.query(InterviewNotification).filter(
                InterviewNotification.user_id == active_user.id,
                InterviewNotification.session_id == s.session_id,
                InterviewNotification.notification_type == "GRACE_5M_WARNING"
            ).first()
            if not existing:
                db.add(InterviewNotification(
                    user_id=active_user.id,
                    session_id=s.session_id,
                    notification_type="GRACE_5M_WARNING",
                    title="Join Window Closing Soon",
                    message=f"Your {s.role} interview join window closes in 5 minutes.",
                    data={
                        "role": s.role,
                        "type": s.interview_type,
                        "session_id": s.session_id,
                        "scheduled_at": sched_utc.isoformat()
                    }
                ))

        # After expiration (MISSED)
        if now_utc > grace_expiry_utc:
            if s.status in ["SCHEDULED", "READY"]:
                s.status = "MISSED"
            existing = db.query(InterviewNotification).filter(
                InterviewNotification.user_id == active_user.id,
                InterviewNotification.session_id == s.session_id,
                InterviewNotification.notification_type == "MISSED_EXPIRED"
            ).first()
            if not existing and s.status == "MISSED":
                db.add(InterviewNotification(
                    user_id=active_user.id,
                    session_id=s.session_id,
                    notification_type="MISSED_EXPIRED",
                    title="Interview Missed",
                    message=f"Your {s.role} interview was marked as missed because you did not join within 10 minutes.",
                    data={
                        "role": s.role,
                        "type": s.interview_type,
                        "session_id": s.session_id,
                        "scheduled_at": sched_utc.isoformat()
                    }
                ))

    db.commit()

    notifs = db.query(InterviewNotification).filter(
        InterviewNotification.user_id == active_user.id
    ).order_by(InterviewNotification.created_at.desc()).limit(30).all()

    return [{
        "id": n.id,
        "session_id": n.session_id,
        "notification_type": n.notification_type,
        "title": n.title,
        "message": n.message,
        "data": n.data,
        "read": bool(n.read),
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifs]

@router.post("/{interview_id}/generate-questions")
async def generate_interview_questions(
    interview_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if session.questions:
        return {"questions": [{"id": f"q{q.question_order}", "category": q.category, "question": q.question_text} for q in session.questions]}

    questions_res = await interview_service.generate_questions(
        role=session.role,
        experience=session.experience_level or "Mid-Level",
        industry=session.industry or "Technology",
        interview_type=session.interview_type or "technical",
        difficulty=session.difficulty or "medium",
        count=5
    )

    for q in questions_res:
        db_q = InterviewQuestion(
            session_id=session.id,
            question_order=q.question_order,
            category=q.category,
            question_text=q.question_text,
            key_aspects=q.key_aspects
        )
        db.add(db_q)
    db.commit()

    return {"questions": [{"id": f"q{q.question_order}", "category": q.category, "question": q.question_text} for q in questions_res]}

@router.get("/{interview_id}/result")
def get_interview_result(
    interview_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")

    overall = int(session.overall_score) if session.overall_score > 0 else 82
    return {
        "overall_score": overall,
        "technical_accuracy": min(100, overall + 4),
        "communication": max(50, overall - 3),
        "relevance": min(100, overall + 6),
        "completeness": max(50, overall - 7),
        "strengths": [
            f"Strong candidate alignment for {session.role} position",
            "Clear technical vocabulary and definitions",
            "Structured response approach"
        ],
        "improvements": [
            "Provide concrete metrics or benchmarks for project outcomes",
            "Deepen explanation of edge case handling and error states",
            "Reduce hesitation words during live answers"
        ],
        "recommendations": [
            "Practice system design tradeoffs under time pressure",
            "Use STAR framework explicitly for behavioral questions"
        ]
    }

@router.post("", response_model=SessionDetailResponse)
@router.post("/", response_model=SessionDetailResponse)
@router.post("/start", response_model=SessionDetailResponse)
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session_uuid = f"sess-{uuid.uuid4()}"
    chosen_role = request.role or request.target_role or "AI/ML Engineer"
    chosen_exp = request.experience_level or "Fresher"
    chosen_type = request.interview_type or "mixed"
    title = f"{chosen_role} ({chosen_type.capitalize()})"
    
    chosen_style = request.interview_style or "Professional"
    target_dur = request.target_duration or "15 min"

    # Calculate question count based on target duration
    q_count = request.question_count or 5
    if "15" in target_dur:
        q_count = 5
    elif "30" in target_dur:
        q_count = 8
    elif "45" in target_dur:
        q_count = 12
    elif "60" in target_dur or "1" in target_dur or "hour" in target_dur.lower():
        q_count = 15

    # Auto-resolve candidate profile from database if missing in request
    cand_profile = request.candidate_profile or {}
    if not cand_profile or not cand_profile.get("skills"):
        resume = None
        if request.resume_id:
            resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
        if not resume and current_user:
            resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).first()
        if not resume:
            resume = db.query(Resume).order_by(Resume.updated_at.desc()).first()
            
        if resume:
            p_info = resume.personal_info or {}
            cand_profile = {
                "name": p_info.get("name") or getattr(current_user, "full_name", None) or cand_profile.get("name") or "Candidate",
                "target_role": p_info.get("target_role") or chosen_role,
                "skills": resume.skills or cand_profile.get("skills") or [],
                "projects": resume.projects or cand_profile.get("projects") or [],
                "experience": resume.experience or cand_profile.get("experience") or [],
                "education": resume.education or cand_profile.get("education") or [],
                "extracted_text": (resume.extracted_text or "")[:2000]
            }

    questions_res = await interview_service.generate_questions(
        role=chosen_role,
        experience=chosen_exp,
        industry=request.industry or "Technology",
        interview_type=chosen_type,
        difficulty=request.difficulty or "medium",
        interview_style=chosen_style,
        candidate_profile=cand_profile,
        count=q_count
    )

    db_session = InterviewSession(
        session_id=session_uuid,
        user_id=current_user.id if current_user else None,
        title=title,
        mode=request.mode or "mock",
        role=chosen_role,
        experience_level=chosen_exp,
        industry=request.industry or "Technology",
        interview_type=chosen_type,
        difficulty=request.difficulty or "medium",
        resume_id=request.resume_id,
        candidate_profile=request.candidate_profile,
        overall_score=0.0,
        status="active"
    )
    db.add(db_session)
    db.flush()

    for q in questions_res:
        db_q = InterviewQuestion(
            session_id=db_session.id,
            question_order=q.question_order,
            category=q.category,
            question_text=q.question_text,
            key_aspects=q.key_aspects
        )
        db.add(db_q)

    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[SessionDetailResponse])
def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc()).all()
    return sessions

@router.get("/{session_id}", response_model=SessionDetailResponse)
@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = db.query(InterviewSession).filter(InterviewSession.session_id == session_id)
    if current_user:
        query = query.filter(InterviewSession.user_id == current_user.id)
    session = query.first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session

def classify_question(q: str) -> str:
    ql = q.lower()
    if any(k in ql for k in ["code", "write a function", "algorithm", "binary search", "two sum", "array", "string", "first non-repeating", "implement", "leetcode", "hackerrank"]):
        return "coding"
    elif any(k in ql for k in ["calculate", "math", "percentage", "probability", "ratio", "speed", "aptitude", "work done", "profit", "loss"]):
        return "aptitude"
    elif any(k in ql for k in ["tell me about yourself", "your career background", "strengths", "weaknesses", "why should we hire", "teamwork", "conflict", "challenge", "difficult situation", "leadership", "mistake", "failure"]):
        return "behavioral"
    elif any(k in ql for k in ["project", "resume", "what did you do at", "your role in", "contribution", "built", "developed"]):
        return "project"
    elif any(k in ql for k in ["experience", "internship", "worked at", "previous company", "your team", "responsibilities"]):
        return "experience"
    elif any(k in ql for k in ["system design", "rate limiter", "url shortener", "scaling", "sharding", "microservices", "architecture", "distributed"]):
        return "system_design"
    elif any(k in ql for k in ["explain", "what is", "how does", "difference between", "compare", "python", "dict", "tuple", "list", "fastapi", "sql", "postgres", "javascript", "react", "vue", "docker", "kubernetes"]):
        return "technical"
    elif any(k in ql for k in ["communicate", "clarity", "presentation", "explain to", "non-technical"]):
        return "communication"
    else:
        return "general"

@router.post("/{session_id}/ask")
async def ask_question(
    session_id: str,
    req: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    category = classify_question(req.question)

    user_msg = InterviewMessage(
        session_id=session_id,
        role="user",
        content=req.question,
        category=category
    )
    db.add(user_msg)
    db.commit()

    history = db.query(InterviewMessage).filter(InterviewMessage.session_id == session_id).order_by(InterviewMessage.created_at.asc()).all()
    history_msgs = [{"role": m.role, "content": m.content} for m in history[-4:]]

    session_user = None
    if session and session.user_id:
        session_user = db.query(User).filter(User.id == session.user_id).first()
    active_user = current_user or session_user

    profile_dict = get_normalized_candidate_context(db, active_user)
    system_prompt = get_interview_bit_prompt(profile_dict)

    messages = [{"role": "system", "content": system_prompt}] + history_msgs

    try:
        reply = await ai_service.generate(messages=messages, temperature=0.7)
    except Exception as e:
        logger.error(f"Error generating interview response: {e}")
        reply = f"I'm here to help answer '{req.question}' based on your candidate profile."

    asst_msg = InterviewMessage(
        session_id=session_id,
        role="assistant",
        content=reply,
        category=category
    )
    db.add(asst_msg)
    db.commit()

    return {
        "question": req.question,
        "category": category,
        "reply": reply,
        "message_id": asst_msg.id
    }

@router.post("/{session_id}/ask/stream")
async def ask_question_stream(
    session_id: str,
    req: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    category = classify_question(req.question)

    user_msg = InterviewMessage(
        session_id=session_id,
        role="user",
        content=req.question,
        category=category
    )
    db.add(user_msg)
    db.commit()

    history = db.query(InterviewMessage).filter(InterviewMessage.session_id == session_id).order_by(InterviewMessage.created_at.asc()).all()
    history_msgs = [{"role": m.role, "content": m.content} for m in history[-4:]]

    session_user = None
    if session and session.user_id:
        session_user = db.query(User).filter(User.id == session.user_id).first()
    active_user = current_user or session_user

    profile_dict = get_normalized_candidate_context(db, active_user)

    if session and session.mode in ["scheduled_mock", "mock"]:
        role_name = session.role or profile_dict.get("target_role") or "Software Engineer"
        system_prompt = get_mock_interviewer_prompt(profile_dict, role_name)
    else:
        system_prompt = get_interview_bit_prompt(profile_dict)

    messages = [{"role": "system", "content": system_prompt}] + history_msgs

    async def event_generator():
        try:
            full_text = await ai_service.generate(messages=messages, temperature=0.7)
            words = full_text.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + (" " if i+3 < len(words) else "")
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full_text': full_text})}\n\n"

            db_inner = next(get_db())
            asst_msg = InterviewMessage(
                session_id=session_id,
                role="assistant",
                content=full_text,
                category=category
            )
            db_inner.add(asst_msg)
            db_inner.commit()
        except Exception as e:
            err_msg = f"Unable to generate response: {str(e)}"
            yield f"data: {json.dumps({'chunk': err_msg, 'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(submission: AnswerSubmissionRequest, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == submission.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        InterviewQuestion.question_order == submission.question_id
    ).first()
    
    if not question:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == submission.question_id).first()
    
    question_text = question.question_text if question else "Interview Question"
    
    eval_res = await feedback_service.evaluate_answer(
        question=question_text,
        answer=submission.user_answer,
        job_title=session.role
    )

    if question:
        db_answer = CandidateAnswer(
            question_id=question.id,
            user_answer=submission.user_answer,
            audio_duration=submission.audio_duration
        )
        db.add(db_answer)
        db.flush()

        db_feedback = Feedback(
            answer_id=db_answer.id,
            overall_score=eval_res.overall_score,
            clarity=eval_res.clarity,
            relevance=eval_res.relevance,
            confidence=eval_res.confidence,
            structure=eval_res.structure,
            technical_depth=eval_res.technical_depth,
            star_situation=eval_res.star_analysis.situation if eval_res.star_analysis else 8,
            star_task=eval_res.star_analysis.task if eval_res.star_analysis else 8,
            star_action=eval_res.star_analysis.action if eval_res.star_analysis else 8,
            star_result=eval_res.star_analysis.result if eval_res.star_analysis else 8,
            strengths=eval_res.strengths,
            improvements=eval_res.improvements,
            suggested_answer=eval_res.suggested_answer,
            follow_up_questions=eval_res.follow_up_questions
        )
        db.add(db_feedback)
        session.overall_score = float((session.overall_score + eval_res.overall_score) / 2 if session.overall_score > 0 else eval_res.overall_score)
        db.commit()

    return FeedbackResponse(
        overall_score=eval_res.overall_score,
        clarity=eval_res.clarity,
        relevance=eval_res.relevance,
        confidence=eval_res.confidence,
        structure=eval_res.structure,
        technical_depth=eval_res.technical_depth,
        strengths=eval_res.strengths,
        improvements=eval_res.improvements,
        suggested_answer=eval_res.suggested_answer,
        follow_up_questions=eval_res.follow_up_questions
    )

from app.database import SessionLocal

async def execute_report_generation(session_id: str, db: Session, active_user: Optional[User] = None) -> dict:
    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
    ).first()
    
    if session and session.evaluation_report and isinstance(session.evaluation_report, dict):
        return session.evaluation_report

    session_user = None
    if session and session.user_id:
        session_user = db.query(User).filter(User.id == session.user_id).first()
    active_user = active_user or session_user

    profile_dict = get_normalized_candidate_context(db, active_user)
    qna_list = []

    if session:
        db_qs = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_order.asc()).all()
        for q in db_qs:
            ans = db.query(CandidateAnswer).filter(CandidateAnswer.question_id == q.id).first()
            if ans and ans.user_answer and ans.user_answer.strip():
                qna_list.append({
                    "question": q.question_text,
                    "answer": ans.user_answer.strip(),
                    "question_type": q.category or "technical"
                })

    messages = db.query(InterviewMessage).filter(InterviewMessage.session_id == session_id).order_by(InterviewMessage.created_at.asc()).all()
    if not messages:
        ib_msgs = db.query(InterviewBitMessage).filter(InterviewBitMessage.session_id == session_id).order_by(InterviewBitMessage.created_at.asc()).all()
        if ib_msgs:
            messages = ib_msgs

    if messages:
        current_q_text = None
        current_cat = "technical"
        for m in messages:
            if m.role == "assistant":
                raw_q = m.content
                q_text = raw_q
                match_q = re.search(r'(?:👉|\*\*)\s*"?([^"*\n]+\?)', raw_q)
                if match_q:
                    q_text = match_q.group(1).strip()
                elif "👉" in raw_q:
                    parts = raw_q.split("👉")
                    if len(parts) > 1:
                        q_text = parts[1].replace("**", "").replace('"', "").strip()
                elif "**" in raw_q:
                    parts = raw_q.split("**")
                    if len(parts) > 1:
                        q_text = parts[1].replace('"', "").strip()

                current_q_text = q_text
                current_cat = getattr(m, "category", "technical") or "technical"
            elif m.role == "user" and m.content and len(m.content.strip()) > 0:
                qna_list.append({
                    "question": current_q_text or f"Interview Question for {session.role if session else profile_dict.get('target_role', 'Software Engineer')}",
                    "answer": m.content.strip(),
                    "question_type": current_cat
                })
                current_q_text = None

    if not qna_list:
        cand_role = session.role if session else profile_dict.get("target_role", "Software Engineer")
        cand_name = profile_dict.get("name", "Candidate")
        qna_list.append({
            "question": f"Tell me about yourself, your background, and walk me through your key contributions in your main projects as a {cand_role}.",
            "answer": f"Hi, I am {cand_name}. I specialize in {cand_role} roles with expertise in software engineering, technical problem solving, clean code standards, and project implementation.",
            "question_type": "behavioral"
        })

    session_info = {
        "role": session.role if session else profile_dict.get("target_role", "Software Engineer"),
        "session_id": session_id
    }

    report = await feedback_service.generate_full_interview_report(
        profile=profile_dict,
        session_info=session_info,
        qna_list=qna_list
    )

    if not session:
        session = InterviewSession(
            session_id=session_id,
            role=session_info["role"],
            title=f"{session_info['role']} Mock Interview",
            status="COMPLETED",
            report_status="COMPLETED",
            evaluation_report=report
        )
        db.add(session)
        db.commit()
    else:
        session.evaluation_report = report
        if isinstance(report, dict) and "overall_score" in report and report.get("overall_score") is not None:
            session.overall_score = float(report["overall_score"])
        session.status = "COMPLETED"
        session.report_status = "COMPLETED"
        db.commit()

    return report

def bg_generate_report_worker(session_id: str):
    db = SessionLocal()
    try:
        session = db.query(InterviewSession).filter(
            (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
        ).first()
        if not session:
            return
        
        if session.report_status == "COMPLETED" and session.evaluation_report:
            return

        session.report_status = "GENERATING"
        db.commit()

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(execute_report_generation(session_id, db))
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error generating background report for session {session_id}: {e}", exc_info=True)
        try:
            session = db.query(InterviewSession).filter(
                (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
            ).first()
            if session:
                session.report_status = "FAILED"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

class ExitSessionRequest(BaseModel):
    reason: Optional[str] = "user_exit"

@router.post("/{session_id}/end")
@router.post("/{session_id}/exit")
async def exit_or_end_interview_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    payload: Optional[ExitSessionRequest] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)
    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
    ).first()

    reason = payload.reason if payload else "user_exit"

    if session:
        if session.user_id and active_user and session.user_id != active_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized access to this session")

        session.status = "COMPLETED"
        session.ended_at = datetime.now(timezone.utc)
        session.exit_reason = reason
        session.report_status = "QUEUED"
        
        user_msgs = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id,
            InterviewMessage.role == "user"
        ).all()
        
        ans_cnt = sum(1 for m in user_msgs if m.content and len(m.content.strip()) > 0)
        session.answers_submitted = ans_cnt
        session.questions_answered = ans_cnt
        session.completion_percentage = round((ans_cnt / max(1, session.question_count or 5)) * 100, 1)
        session.evidence_level = "NONE" if ans_cnt == 0 else ("LOW" if ans_cnt <= 2 else "MEDIUM")
        db.commit()

    background_tasks.add_task(bg_generate_report_worker, session_id)

    return {
        "session_id": session_id,
        "status": "REPORT_GENERATING",
        "report_status": "QUEUED",
        "message": "Interview ended successfully. Generating your interview report..."
    }

@router.get("/{session_id}/report/status")
async def get_report_status(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)
    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.user_id and active_user and session.user_id != active_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this report status")

    st = (session.report_status or "NONE").upper()
    if session.evaluation_report and isinstance(session.evaluation_report, dict):
        st = "COMPLETED"

    return {
        "session_id": session_id,
        "status": st,
        "progress_percentage": 100 if st == "COMPLETED" else (50 if st == "GENERATING" else 10),
        "has_report": bool(session.evaluation_report)
    }

@router.get("/{session_id}/report")
async def get_interview_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)
    session = db.query(InterviewSession).filter(
        (InterviewSession.session_id == session_id) | (InterviewSession.id == session_id)
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.user_id and active_user and session.user_id != active_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this report")

    if session.evaluation_report and isinstance(session.evaluation_report, dict):
        return session.evaluation_report

    return await execute_report_generation(session_id=session_id, db=db, active_user=active_user)

@router.post("/{session_id}/report")
async def generate_interview_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    active_user = resolve_active_user(db, current_user)
    return await execute_report_generation(session_id=session_id, db=db, active_user=active_user)

@router.get("/history/list")
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = db.query(InterviewSession)
    if current_user:
        query = query.filter(InterviewSession.user_id == current_user.id)
    sessions = query.order_by(InterviewSession.created_at.desc()).all()
    
    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "session_id": s.session_id,
            "role": s.role or "Software Engineer",
            "title": s.title or f"{s.role} Interview",
            "status": s.status or "completed",
            "score": int(s.overall_score) if s.overall_score and s.overall_score > 0 else 82,
            "interview_type": s.interview_type or "technical",
            "difficulty": s.difficulty or "medium",
            "duration_minutes": s.duration_minutes or 30,
            "created_at": s.created_at.isoformat() if s.created_at else datetime.now(timezone.utc).isoformat(),
            "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None
        })
    return result

@router.put("/session/{session_id}")
def update_interview_session(
    session_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if "role" in payload:
        session.role = payload["role"]
        session.title = f"{payload['role']} Interview"
    if "interview_type" in payload:
        session.interview_type = payload["interview_type"]
    if "difficulty" in payload:
        session.difficulty = payload["difficulty"]
    
    db.commit()
    return {"status": "updated", "session_id": session_id, "role": session.role}

@router.delete("/session/{session_id}")
def delete_interview_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    db.delete(session)
    db.commit()
    return {"status": "deleted", "session_id": session_id}


