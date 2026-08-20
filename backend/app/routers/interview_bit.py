import os
import uuid
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.interview_bit import CandidateProfile, InterviewBitSession, InterviewBitMessage
from app.schemas.interview_bit import (
    CandidateProfileCreate, CandidateProfileUpdate, CandidateProfileResponse,
    ResumeUploadResponse, InterviewBitAskRequest, InterviewBitAskResponse,
    InterviewBitMessageResponse, InterviewBitSessionResponse
)
from app.security import get_current_user, get_current_user_required
from app.services.resume_service import resume_service
from app.services.interview_bit_service import interview_bit_service
from app.services.ai_service import ai_service
from app.prompts.interview_bit import get_interview_bit_prompt
from app.services.profile_normalizer import get_normalized_candidate_context, deduplicate_items

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview-bit", tags=["Interview Bit"])

@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_interview_bit_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Use PDF, DOCX, or TXT.")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")

    try:
        extracted = await resume_service.build_candidate_profile(file_bytes, file.filename)
    except Exception as e:
        logger.error(f"Error parsing resume in Interview Bit: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    prof = extracted["profile"]
    raw_text = extracted.get("raw_text", "")
    profile_id = str(uuid.uuid4())

    # Save to main Resume table if user logged in
    if current_user:
        new_resume = Resume(
            user_id=current_user.id,
            title=f"{prof.get('name', 'Candidate')} - {prof.get('target_role', 'Developer')} Resume",
            filename=file.filename,
            extracted_text=raw_text,
            personal_info={
                "name": prof.get("name", "Candidate"),
                "email": prof.get("email", ""),
                "phone": prof.get("phone", ""),
                "target_role": prof.get("target_role", "Developer"),
                "experience_level": prof.get("experience_level", "Fresher"),
                "location": prof.get("location", "")
            },
            summary=f"Parsed from {file.filename}.",
            skills=prof.get("skills", []),
            projects=prof.get("projects", []),
            education=prof.get("education", []),
            certifications=prof.get("certifications", []),
            is_primary=True
        )
        db.add(new_resume)

    db_profile = CandidateProfile(
        id=profile_id,
        user_id=current_user.id if current_user else None,
        name=prof.get("name", "Candidate"),
        email=prof.get("email"),
        phone=prof.get("phone"),
        target_role=prof.get("target_role", "Backend Developer"),
        experience_level=prof.get("experience_level", "Fresher"),
        skills=prof.get("skills", []),
        languages=prof.get("programming_languages", ["Python", "JavaScript"]),
        frameworks=prof.get("frameworks", ["FastAPI"]),
        databases=prof.get("databases", ["PostgreSQL"]),
        cloud=prof.get("cloud", ["Docker"]),
        projects=prof.get("projects", []),
        education=prof.get("education", []),
        certifications=prof.get("certifications", []),
        resume_filename=file.filename,
        additional_information=f"Parsed from {file.filename}."
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return {
        "resume_id": extracted["resume_id"],
        "profile": db_profile
    }

@router.post("/profile", response_model=CandidateProfileResponse)
async def save_profile(
    profile_in: CandidateProfileCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    profile_id = str(uuid.uuid4())
    db_profile = CandidateProfile(
        id=profile_id,
        user_id=current_user.id if current_user else None,
        name=profile_in.name or "Candidate",
        email=profile_in.email,
        phone=profile_in.phone,
        target_role=profile_in.target_role or "Backend Developer",
        experience_level=profile_in.experience_level or "Fresher",
        location=profile_in.location or "",
        skills=profile_in.skills or [],
        languages=profile_in.languages or [],
        frameworks=profile_in.frameworks or [],
        databases=profile_in.databases or [],
        cloud=profile_in.cloud or [],
        projects=profile_in.projects or [],
        education=profile_in.education or [],
        certifications=profile_in.certifications or [],
        achievements=profile_in.achievements or [],
        additional_information=profile_in.additional_information or "",
        resume_filename=profile_in.resume_filename
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profile", response_model=CandidateProfileResponse)
async def get_latest_profile(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # 1. Fetch user's active/primary resume from the main resumes table
    user_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.is_primary.desc(), Resume.updated_at.desc()).first()
    
    # 2. Check existing CandidateProfile
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).order_by(CandidateProfile.created_at.desc()).first()

    if user_resume:
        p_info = user_resume.personal_info or {}
        name = p_info.get("name") or getattr(current_user, "full_name", None) or getattr(current_user, "name", None) or "Candidate"
        target_role = p_info.get("target_role") or current_user.target_role or "Software Engineer"
        experience_level = p_info.get("experience_level") or current_user.experience_level or "Fresher"
        location = p_info.get("location") or ""
        email = p_info.get("email") or current_user.email
        phone = p_info.get("phone") or ""

        if not profile:
            profile = CandidateProfile(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                name=name,
                email=email,
                phone=phone,
                target_role=target_role,
                experience_level=experience_level,
                location=location,
                skills=user_resume.skills or [],
                projects=user_resume.projects or [],
                experience=user_resume.experience or [],
                education=user_resume.education or [],
                certifications=user_resume.certifications or [],
                achievements=user_resume.achievements or [],
                resume_filename=user_resume.filename,
                additional_information=user_resume.summary or ""
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        else:
            # Sync latest resume changes to profile
            profile.name = name
            profile.target_role = target_role
            profile.experience_level = experience_level
            profile.location = location
            profile.skills = user_resume.skills or profile.skills
            profile.projects = user_resume.projects or profile.projects
            profile.experience = user_resume.experience or profile.experience
            profile.education = user_resume.education or profile.education
            profile.certifications = user_resume.certifications or profile.certifications
            profile.achievements = user_resume.achievements or profile.achievements
            profile.resume_filename = user_resume.filename
            profile.additional_information = user_resume.summary or profile.additional_information
            db.commit()
            db.refresh(profile)
        return profile

    if not profile:
        profile = CandidateProfile(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=getattr(current_user, "full_name", None) or getattr(current_user, "name", None) or "Candidate",
            target_role=current_user.target_role or "Software Engineer",
            experience_level=current_user.experience_level or "Fresher",
            skills=[],
            projects=[],
            education=[],
            certifications=[],
            achievements=[]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile

@router.get("/profile/{profile_id}", response_model=CandidateProfileResponse)
async def get_profile_by_id(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id, CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return profile

@router.put("/profile/{profile_id}", response_model=CandidateProfileResponse)
async def update_profile(
    profile_id: str,
    profile_in: CandidateProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id, CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    for field, val in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile

@router.post("/ask", response_model=InterviewBitAskResponse)
async def ask_interview_bit(
    req: InterviewBitAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    # Retrieve profile
    profile_dict = get_normalized_candidate_context(db, current_user, req.profile_id)
    profile_id = profile_dict.get("id") or req.profile_id

    # Session management
    session_id = req.session_id
    session_obj = None
    if session_id:
        session_obj = db.query(InterviewBitSession).filter(
            InterviewBitSession.session_id == session_id,
            InterviewBitSession.user_id == current_user.id
        ).first()

    if not session_obj:
        session_id = f"ib-{uuid.uuid4()}"
        session_obj = InterviewBitSession(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            profile_id=profile_id,
            title="New Chat"
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

    # Auto-generate smart title on first message
    if session_obj.title in ["New Chat", "Interview Bit Practice", ""] or session_obj.title.startswith("Practice:"):
        words = [w for w in req.question.strip().split() if len(w) > 2]
        title_text = " ".join(words[:6]).title() if words else req.question[:40]
        session_obj.title = title_text[:50]
        db.commit()

    # Load history
    history_records = db.query(InterviewBitMessage).filter(InterviewBitMessage.session_id == session_id).order_by(InterviewBitMessage.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in history_records[-6:]]

    # Save user message
    classification = interview_bit_service.classify(req.question)
    cat = classification.get("category", "general")

    user_msg = InterviewBitMessage(
        session_id=session_id,
        role="user",
        content=req.question,
        category=cat
    )
    db.add(user_msg)
    db.commit()

    result = await interview_bit_service.generate_answer(
        question=req.question,
        profile=profile_dict,
        history=history,
        style=req.style or "normal"
    )

    # Save assistant message
    asst_msg = InterviewBitMessage(
        session_id=session_id,
        role="assistant",
        content=result["answer"],
        category=result["category"]
    )
    db.add(asst_msg)
    db.commit()

    return {
        "question": req.question,
        "category": result["category"],
        "answer": result["answer"],
        "profile_used": result["profile_used"],
        "session_id": session_id,
        "follow_ups": result["follow_ups"]
    }

@router.post("/ask/stream")
async def ask_interview_bit_stream(
    req: InterviewBitAskRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    profile_dict = get_normalized_candidate_context(db, current_user, req.profile_id)
    profile_id = profile_dict.get("id") or req.profile_id

    session_id = req.session_id
    if not session_id:
        session_id = f"ib-{uuid.uuid4()}"
        session = InterviewBitSession(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            profile_id=profile_id,
            title=f"Practice: {req.question[:30]}"
        )
        db.add(session)
        db.commit()

    history_records = db.query(InterviewBitMessage).filter(InterviewBitMessage.session_id == session_id).order_by(InterviewBitMessage.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in history_records[-6:]]

    classification = interview_bit_service.classify(req.question)
    cat = classification.get("category", "general")

    user_msg = InterviewBitMessage(
        session_id=session_id,
        role="user",
        content=req.question,
        category=cat
    )
    db.add(user_msg)
    db.commit()

    system_prompt = get_interview_bit_prompt(profile_dict, req.style or "normal")
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": req.question}]

    async def event_generator():
        full_text = ""
        try:
            async for token_chunk in ai_service.generate_stream(messages=messages, temperature=0.7):
                full_text += token_chunk
                yield f"data: {json.dumps({'chunk': token_chunk, 'session_id': session_id, 'category': cat})}\n\n"

            follow_ups = interview_bit_service.generate_follow_ups(cat, req.question)
            yield f"data: {json.dumps({'done': True, 'full_text': full_text, 'follow_ups': follow_ups, 'session_id': session_id})}\n\n"

            db_inner = next(get_db())
            asst_msg = InterviewBitMessage(
                session_id=session_id,
                role="assistant",
                content=full_text,
                category=cat
            )
            db_inner.add(asst_msg)
            db_inner.commit()
        except Exception as e:
            err_msg = f"Unable to generate response: {str(e)}"
            yield f"data: {json.dumps({'chunk': err_msg, 'done': True, 'session_id': session_id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/sessions", response_model=List[InterviewBitSessionResponse])
async def get_user_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Retrieve all chat sessions belonging to current user."""
    sessions = db.query(InterviewBitSession).filter(
        InterviewBitSession.user_id == current_user.id
    ).order_by(InterviewBitSession.updated_at.desc(), InterviewBitSession.created_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=InterviewBitSessionResponse)
async def create_chat_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Create a new empty chat session for current user."""
    session_id = f"ib-{uuid.uuid4()}"
    new_sess = InterviewBitSession(
        session_id=session_id,
        user_id=current_user.id,
        title="New Chat"
    )
    db.add(new_sess)
    db.commit()
    db.refresh(new_sess)
    return new_sess

@router.get("/sessions/{session_id}", response_model=InterviewBitSessionResponse)
async def get_chat_session_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get chat session details and message history for current user."""
    sess = db.query(InterviewBitSession).filter(
        InterviewBitSession.session_id == session_id,
        InterviewBitSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return sess

@router.patch("/sessions/{session_id}")
async def rename_chat_session(
    session_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Rename a chat session."""
    title = payload.get("title", "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    sess = db.query(InterviewBitSession).filter(
        InterviewBitSession.session_id == session_id,
        InterviewBitSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")

    sess.title = title[:60]
    db.commit()
    return {"status": "success", "session_id": session_id, "title": sess.title}

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Delete a chat session and all its messages."""
    sess = db.query(InterviewBitSession).filter(
        InterviewBitSession.session_id == session_id,
        InterviewBitSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Delete all associated messages first
    db.query(InterviewBitMessage).filter(InterviewBitMessage.session_id == session_id).delete(synchronize_session=False)
    db.delete(sess)
    db.commit()
    return {"status": "deleted", "session_id": session_id}

@router.post("/sessions/{session_id}/attach-resume/{resume_id}")
async def attach_resume_to_session(
    session_id: str,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Attach an existing resume owned by current user to a chat session."""
    sess = db.query(InterviewBitSession).filter(
        InterviewBitSession.session_id == session_id,
        InterviewBitSession.user_id == current_user.id
    ).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")

    res_obj = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not res_obj:
        raise HTTPException(status_code=404, detail="Resume not found")

    sess.active_resume_id = res_obj.id
    db.commit()
    return {"status": "attached", "session_id": session_id, "resume_id": res_obj.id, "filename": res_obj.filename}
