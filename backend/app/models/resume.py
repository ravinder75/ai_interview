from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False, default="My Resume")
    filename = Column(String, nullable=False, default="resume.pdf")
    template_id = Column(String, nullable=False, default="modern_ats")
    version_name = Column(String, nullable=False, default="Original")
    is_primary = Column(Boolean, default=False)
    
    extracted_text = Column(Text, nullable=True)
    personal_info = Column(JSON, default=dict) # name, email, phone, location, linkedin, github, role, experience_level
    summary = Column(Text, nullable=True)
    experience = Column(JSON, default=list) # [{role, company, duration, description}]
    education = Column(JSON, default=list) # [{degree, institution, year}]
    skills = Column(JSON, default=list) # ["Python", "FastAPI"]
    projects = Column(JSON, default=list) # [{name, technologies, description}]
    certifications = Column(JSON, default=list) # ["AWS Certified"]
    achievements = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    links = Column(JSON, default=list)
    
    ats_score = Column(Integer, default=85)
    metrics = Column(JSON, default=dict)
    analytics = Column(JSON, default=dict)
    issues = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=False)
    skills = Column(JSON, default=list)
    experience_summary = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    potential_questions = Column(JSON, default=list)
    preparation_topics = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
