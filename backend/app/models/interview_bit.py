import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CandidateProfile(Base):
    __tablename__ = "interview_bit_candidate_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, default="Candidate")
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    target_role = Column(String, default="Backend Developer")
    experience_level = Column(String, default="Fresher")
    location = Column(String, default="")
    skills = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    frameworks = Column(JSON, default=list)
    databases = Column(JSON, default=list)
    cloud = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    additional_information = Column(Text, default="")
    resume_filename = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("InterviewBitSession", back_populates="profile", cascade="all, delete-orphan")

class InterviewBitSession(Base):
    __tablename__ = "interview_bit_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: f"ib-{uuid.uuid4()}")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    profile_id = Column(String, ForeignKey("interview_bit_candidate_profiles.id"), nullable=True)
    active_resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile = relationship("CandidateProfile", back_populates="sessions")
    messages = relationship("InterviewBitMessage", back_populates="session", cascade="all, delete-orphan")

class InterviewBitMessage(Base):
    __tablename__ = "interview_bit_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_bit_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False) # user | assistant | system
    content = Column(Text, nullable=False)
    category = Column(String, default="general")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewBitSession", back_populates="messages")
