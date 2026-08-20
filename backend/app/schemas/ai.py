from pydantic import BaseModel, Field
from typing import List, Optional

class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    job_title: Optional[str] = "Software Engineer"
    job_description: Optional[str] = ""

class StarScore(BaseModel):
    situation: int = Field(default=8, ge=0, le=10)
    task: int = Field(default=8, ge=0, le=10)
    action: int = Field(default=8, ge=0, le=10)
    result: int = Field(default=8, ge=0, le=10)

class AnswerEvaluationResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    relevance: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    technical_depth: int = Field(..., ge=0, le=100)
    star_analysis: Optional[StarScore] = None
    strengths: List[str] = []
    improvements: List[str] = []
    suggested_answer: str
    follow_up_questions: List[str] = []

class ResumeAnswerRequest(BaseModel):
    question: str
    role: Optional[str] = "Senior Software Engineer"
    resume_text: str

class ResumeAnswerResponse(BaseModel):
    generated_answer: str
    key_talking_points: List[str] = []

class ChatMessage(BaseModel):
    role: str # user or assistant or system
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    reply: str
