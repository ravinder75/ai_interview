from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScheduleInterviewRequest(BaseModel):
    role: str = Field("Software Engineer")
    type: Optional[str] = Field("technical_behavioral")
    interview_type: Optional[str] = None
    difficulty: Optional[str] = Field("medium")
    scheduled_at: Optional[Any] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(30)
    programming_language: Optional[str] = "Python"
    resume_id: Optional[str] = None
    timezone: Optional[str] = "UTC"

class ScheduledInterviewResponse(BaseModel):
    id: str
    status: str
    role: str
    type: str
    difficulty: str
    scheduled_at: Optional[datetime] = None
    duration_minutes: int
    programming_language: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionGenerateRequest(BaseModel):
    role: str = "AI/ML Engineer"
    experience: str = "Fresher"
    industry: str = "Technology"
    interview_type: str = "technical"
    difficulty: str = "medium"
    count: int = 5

class QuestionResponse(BaseModel):
    id: Optional[int] = None
    question_order: int
    category: str
    question_text: str
    key_aspects: List[str] = []

    class Config:
        from_attributes = True

class StartSessionRequest(BaseModel):
    role: Optional[str] = "AI/ML Engineer"
    target_role: Optional[str] = None
    experience_level: Optional[str] = "Fresher"
    industry: Optional[str] = "Technology"
    mode: Optional[str] = "mock"
    interview_type: Optional[str] = "mixed"
    difficulty: Optional[str] = "medium"
    interview_style: Optional[str] = "Professional"
    target_duration: Optional[str] = "15 min"
    question_count: Optional[int] = 5
    resume_id: Optional[str] = None
    candidate_profile: Optional[Dict[str, Any]] = None

class AskQuestionRequest(BaseModel):
    question: str

class MessageResponse(BaseModel):
    id: Optional[int] = None
    session_id: str
    role: str
    content: str
    category: str = "general"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnswerSubmissionRequest(BaseModel):
    session_id: str
    question_id: int
    user_answer: str
    audio_duration: float = 0.0

class FeedbackResponse(BaseModel):
    overall_score: Optional[int] = None
    clarity: Optional[int] = None
    relevance: Optional[int] = None
    confidence: Optional[int] = None
    structure: Optional[int] = None
    technical_depth: Optional[int] = None
    strengths: List[str] = []
    improvements: List[str] = []
    suggested_answer: Optional[str] = None
    follow_up_questions: List[str] = []

    class Config:
        from_attributes = True

class InterviewResultResponse(BaseModel):
    overall_score: Optional[int] = None
    technical_accuracy: Optional[int] = None
    communication: Optional[int] = None
    relevance: Optional[int] = None
    completeness: Optional[int] = None
    strengths: List[str] = []
    improvements: List[str] = []
    recommendations: List[str] = []

class SessionDetailResponse(BaseModel):
    id: int
    session_id: str
    title: str
    mode: str
    role: str
    experience_level: str
    industry: str
    interview_type: str
    difficulty: str
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = 30
    programming_language: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    exit_reason: Optional[str] = None
    question_count: Optional[int] = 5
    questions_presented: Optional[int] = 0
    questions_answered: Optional[int] = 0
    questions_skipped: Optional[int] = 0
    answers_submitted: Optional[int] = 0
    completion_percentage: Optional[float] = 0.0
    report_status: Optional[str] = "NONE"
    evidence_level: Optional[str] = "NONE"
    overall_score: Optional[float] = None
    status: str
    resume_id: Optional[str] = None
    candidate_profile: Optional[Dict[str, Any]] = None
    created_at: datetime
    questions: List[QuestionResponse] = []
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
