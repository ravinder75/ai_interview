from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resume_id = Column(String, nullable=True)
    candidate_profile = Column(JSON, nullable=True)
    title = Column(String, nullable=False)
    mode = Column(String, default="practice")
    role = Column(String, nullable=False)
    experience_level = Column(String, default="Mid-Level")
    industry = Column(String, default="Technology")
    interview_type = Column(String, default="technical")
    difficulty = Column(String, default="medium")
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=30)
    programming_language = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    exit_reason = Column(String, nullable=True)
    question_count = Column(Integer, default=5)
    questions_presented = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    questions_skipped = Column(Integer, default=0)
    answers_submitted = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    report_status = Column(String, default="NONE")
    evidence_level = Column(String, default="NONE")
    report_generated_at = Column(DateTime(timezone=True), nullable=True)
    evidence_hash = Column(String, nullable=True)
    overall_score = Column(Float, nullable=True)
    evaluation_report = Column(JSON, nullable=True)
    timezone = Column(String, default="UTC")
    status = Column(String, default="SCHEDULED")  # SCHEDULED, READY, IN_PROGRESS, EXITED, ABANDONED, COMPLETED, MISSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("InterviewMessage", back_populates="session", cascade="all, delete-orphan")

class InterviewNotification(Base):
    __tablename__ = "interview_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    notification_type = Column(String(100), nullable=False) # REMINDER_30M, READY_START, GRACE_5M_WARNING, MISSED_EXPIRED
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    read = Column(Integer, default=0) # 0 = unread, 1 = read
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    category = Column(String, default="general")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="messages")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)
    category = Column(String, default="Technical")
    question_text = Column(Text, nullable=False)
    key_aspects = Column(JSON, default=list)
    question_status = Column(String, default="DISPLAYED") # DISPLAYED, ANSWERED, SKIPPED, UNANSWERED, CANCELLED

    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("CandidateAnswer", back_populates="question", cascade="all, delete-orphan")

class CandidateAnswer(Base):
    __tablename__ = "candidate_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    transcript = Column(Text, nullable=True)
    audio_duration = Column(Float, default=0.0)
    answer_status = Column(String, default="ANSWERED") # EMPTY, SKIPPED, ANSWERED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("InterviewQuestion", back_populates="answers")
    feedback = relationship("Feedback", back_populates="answer", uselist=False, cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("candidate_answers.id"), nullable=False)
    overall_score = Column(Integer, default=75)
    clarity = Column(Integer, default=75)
    relevance = Column(Integer, default=75)
    confidence = Column(Integer, default=75)
    structure = Column(Integer, default=75)
    technical_depth = Column(Integer, default=75)
    
    star_situation = Column(Integer, default=8)
    star_task = Column(Integer, default=8)
    star_action = Column(Integer, default=8)
    star_result = Column(Integer, default=8)

    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    suggested_answer = Column(Text, nullable=True)
    follow_up_questions = Column(JSON, default=list)

    answer = relationship("CandidateAnswer", back_populates="feedback")
