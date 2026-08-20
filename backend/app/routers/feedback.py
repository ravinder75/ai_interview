from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview import Feedback, CandidateAnswer, InterviewQuestion, InterviewSession
from app.schemas.interview import FeedbackResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["Feedback History"])

@router.get("/session/{session_id}", response_model=List[FeedbackResponse])
def get_session_feedback(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).all()
    question_ids = [q.id for q in questions]
    
    answers = db.query(CandidateAnswer).filter(CandidateAnswer.question_id.in_(question_ids)).all()
    answer_ids = [a.id for a in answers]
    
    feedbacks = db.query(Feedback).filter(Feedback.answer_id.in_(answer_ids)).all()
    return feedbacks
