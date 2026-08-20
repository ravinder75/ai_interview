from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base

class JobDescriptionAnalysis(Base):
    __tablename__ = "job_description_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    job_description_text = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    likely_interview_topics = Column(JSON, default=list)
    personalized_prep_plan = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    canonical_job_id = Column(String(255), index=True, nullable=True)
    fingerprint = Column(String(255), unique=True, index=True, nullable=True)
    company = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    location = Column(String(255), default="Remote", index=True)
    country = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    work_mode = Column(String(100), default="Remote", index=True) # Remote / Hybrid / On-site
    job_type = Column(String(100), default="Full-time", index=True) # Full-time / Internship / Freelance / Contract / Part-time / Temporary / Apprenticeship / Graduate / Other
    experience_level = Column(String(100), default="Mid-Level", index=True) # Fresher / Internship / Entry Level / Junior / Mid Level / Senior / Lead / Manager
    category = Column(String(255), default="Software Development", index=True)
    salary_range = Column(String(255), nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="USD")
    description = Column(Text, nullable=False)
    skills = Column(JSON, default=list)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    sources_json = Column(JSON, default=list) # Merged sources e.g. ["Greenhouse", "Lever"]
    posted_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(255), default="Direct Careers")
    application_url = Column(String(1000), nullable=False)
    canonical_url = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserJobProfile(Base):
    __tablename__ = "user_job_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    skills = Column(JSON, default=list)
    frameworks = Column(JSON, default=list)
    databases = Column(JSON, default=list)
    roles = Column(JSON, default=list)
    experience_years = Column(Float, default=0.0)
    education = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    locations = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    status = Column(String(100), default="Applied") # Saved / Applied / Interview / Rejected / Offer
    source = Column(String(255), default="Direct Careers")
    application_url = Column(String(1000), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

class ApplicationClick(Base):
    __tablename__ = "application_clicks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    source = Column(String(255), default="Direct Careers")
    application_url = Column(String(1000), nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

class JobNotification(Base):
    __tablename__ = "job_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    canonical_job_id = Column(String(255), nullable=True)
    match_score = Column(Integer, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
