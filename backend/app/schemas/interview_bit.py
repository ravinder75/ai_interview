from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectItem(BaseModel):
    name: str
    technologies: List[str] = []
    description: Optional[str] = ""

class CandidateProfileBase(BaseModel):
    name: Optional[str] = "Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    target_role: Optional[str] = "Backend Developer"
    experience_level: Optional[str] = "Fresher"
    location: Optional[str] = None
    skills: List[str] = []
    languages: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud: List[str] = []
    projects: List[Any] = []
    experience: List[Any] = []
    education: List[Any] = []
    certifications: List[Any] = []
    achievements: List[Any] = []
    additional_information: Optional[str] = ""
    resume_filename: Optional[str] = None

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileUpdate(CandidateProfileBase):
    pass

class CandidateProfileResponse(CandidateProfileBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    resume_id: str
    profile: CandidateProfileResponse

class InterviewBitAskRequest(BaseModel):
    question: str
    profile_id: Optional[str] = None
    session_id: Optional[str] = None
    style: Optional[str] = "normal" # concise | normal | detailed

class InterviewBitAskResponse(BaseModel):
    question: str
    category: str
    answer: str
    profile_used: bool
    session_id: str
    follow_ups: List[str] = []

class InterviewBitMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewBitSessionResponse(BaseModel):
    id: int
    session_id: str
    profile_id: Optional[str] = None
    active_resume_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[InterviewBitMessageResponse] = []

    class Config:
        from_attributes = True
