from app.routers.auth import router as auth_router
from app.routers.interviews import router as interviews_router
from app.routers.questions import router as questions_router
from app.routers.ai import router as ai_router
from app.routers.resumes import router as resumes_router
from app.routers.jobs import router as jobs_router
from app.routers.feedback import router as feedback_router
from app.routers.settings import router as settings_router
from app.routers.interview_bit import router as interview_bit_router
from app.routers.mock_interviews import router as mock_interviews_router

__all__ = [
    "auth_router",
    "interviews_router",
    "questions_router",
    "ai_router",
    "resumes_router",
    "jobs_router",
    "feedback_router",
    "settings_router",
    "interview_bit_router",
    "mock_interviews_router"
]
