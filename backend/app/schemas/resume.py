from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    title: Optional[str] = "My Resume"
    filename: Optional[str] = "resume.pdf"
    template_id: Optional[str] = "modern_ats"
    version_name: Optional[str] = "Original"
    is_primary: Optional[bool] = False
    personal_info: Optional[Dict[str, Any]] = {}
    summary: Optional[str] = ""
    experience: Optional[List[Any]] = []
    education: Optional[List[Any]] = []
    skills: Optional[List[str]] = []
    projects: Optional[List[Any]] = []
    certifications: Optional[List[Any]] = []
    achievements: Optional[List[Any]] = []
    languages: Optional[List[Any]] = []
    links: Optional[List[Any]] = []

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    pass

class ProjectDetail(BaseModel):
    name: str
    technologies: List[str] = []
    description: Optional[str] = ""

class CandidateProfile(BaseModel):
    name: Optional[str] = "Candidate"
    target_role: str = "Backend Developer"
    experience_level: str = "Fresher"
    education: List[str] = []
    skills: List[str] = []
    languages: List[str] = ["English"]
    projects: List[ProjectDetail] = []
    experience: List[str] = []
    certifications: List[str] = []

class ResumeAnalyzeResponse(BaseModel):
    id: Optional[int] = None
    filename: str
    skills: List[str]
    experience_summary: str
    strengths: List[str]
    missing_skills: List[str]
    potential_questions: List[str]
    preparation_topics: List[str]
    candidate_profile: Optional[CandidateProfile] = None
    created_at: Optional[datetime] = None

class ResumeResponse(ResumeBase):
    id: int
    user_id: Optional[int] = None
    extracted_text: Optional[str] = ""
    ats_score: Optional[int] = 85
    metrics: Optional[Dict[str, Any]] = {}
    analytics: Optional[Dict[str, Any]] = {}
    issues: Optional[List[Dict[str, Any]]] = []
    strengths: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResumeJobMatchRequest(BaseModel):
    job_description: str

class ResumeFixRequest(BaseModel):
    issue_ids: Optional[List[str]] = [] # Fix specific or all
    fix_all: Optional[bool] = False

class ResumeApplyTemplateRequest(BaseModel):
    template_id: str
    template_name: str
