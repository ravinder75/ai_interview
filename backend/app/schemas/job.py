from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobAnalyzeRequest(BaseModel):
    job_title: str
    company_name: Optional[str] = ""
    job_description_text: str

class JobAnalyzeResponse(BaseModel):
    id: Optional[int] = None
    job_title: str
    company_name: Optional[str] = ""
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    keywords: List[str]
    likely_interview_topics: List[str]
    personalized_prep_plan: List[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
