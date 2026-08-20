import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import Base, engine
# Import all models so create_all() picks them up
from app.models import User, PasswordReset  # noqa: F401
from app.routers import (
    auth_router,
    interviews_router,
    questions_router,
    ai_router,
    resumes_router,
    jobs_router,
    feedback_router,
    settings_router,
    interview_bit_router,
    mock_interviews_router
)
from app.websocket import ws_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("interview-coach-ai")

from sqlalchemy import inspect, text

# Create database tables automatically
Base.metadata.create_all(bind=engine)

def auto_migrate_db():
    """Inspect SQLite database tables and automatically alter missing columns."""
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            # Migrate interview_sessions table
            if "interview_sessions" in table_names:
                existing = [c["name"] for c in inspector.get_columns("interview_sessions")]
                expected_columns = {
                    "candidate_profile": "TEXT",
                    "mode": "VARCHAR DEFAULT 'practice'",
                    "exit_reason": "VARCHAR",
                    "questions_presented": "INTEGER DEFAULT 0",
                    "questions_answered": "INTEGER DEFAULT 0",
                    "questions_skipped": "INTEGER DEFAULT 0",
                    "answers_submitted": "INTEGER DEFAULT 0",
                    "completion_percentage": "FLOAT DEFAULT 0.0",
                    "report_status": "VARCHAR DEFAULT 'NONE'",
                    "evidence_level": "VARCHAR DEFAULT 'NONE'",
                    "report_generated_at": "DATETIME",
                    "evidence_hash": "VARCHAR",
                    "overall_score": "FLOAT",
                    "evaluation_report": "TEXT"
                }
                for col_name, col_type in expected_columns.items():
                    if col_name not in existing:
                        try:
                            conn.execute(text(f"ALTER TABLE interview_sessions ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"✅ Auto-migrated SQLite column 'interview_sessions.{col_name}'")
                        except Exception as ex:
                            logger.warning(f"Notice migrating column {col_name}: {ex}")

            # Migrate interview_questions table
            if "interview_questions" in table_names:
                existing = [c["name"] for c in inspector.get_columns("interview_questions")]
                expected_q_columns = {
                    "sample_answer": "TEXT",
                    "difficulty": "VARCHAR",
                    "question_type": "VARCHAR"
                }
                for col_name, col_type in expected_q_columns.items():
                    if col_name not in existing:
                        try:
                            conn.execute(text(f"ALTER TABLE interview_questions ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"✅ Auto-migrated SQLite column 'interview_questions.{col_name}'")
                        except Exception as ex:
                            logger.warning(f"Notice migrating column {col_name}: {ex}")

    except Exception as err:
        logger.warning(f"Automatic DB schema migration notice: {err}")

auto_migrate_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-quality AI Interview Practice & Coaching Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

# Include Routers
app.include_router(auth_router)
app.include_router(interviews_router)
app.include_router(mock_interviews_router)
app.include_router(questions_router)
app.include_router(ai_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(feedback_router)
app.include_router(settings_router)
app.include_router(interview_bit_router)
app.include_router(ws_router)

from fastapi.responses import JSONResponse, FileResponse

# Mount Assistant Floating Window static path
extension_window_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../interview-bit-extension/dist/src/window"))
if os.path.exists(extension_window_dir):
    app.mount("/assistant", StaticFiles(directory=extension_window_dir, html=True), name="assistant")

# Health & Status Endpoints
@app.get("/", tags=["Health"])
def root():
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "ai_provider_base_url": settings.AI_BASE_URL,
        "ai_model": settings.AI_MODEL,
        "google_oauth_configured": settings.google_oauth_configured,
    }

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": exc.__class__.__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
