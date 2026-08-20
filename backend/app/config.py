import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Interview Coach AI"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "mysql+pymysql://root:admin1123@localhost:3306/interview_coach?charset=utf8mb4"

    AI_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

    @property
    def AI_API_KEY(self) -> str:
        return self.OPENROUTER_API_KEY

    @property
    def AI_MODEL(self) -> str:
        return self.OPENROUTER_MODEL

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8090,http://127.0.0.1:8090"

    JWT_SECRET: str = "replace-with-long-random-secret-at-least-32-chars"
    JWT_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8005/api/auth/google/callback"

    # Password reset & Email SMTP Configuration
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.environ.get("SMTP_USERNAME", "ravinderkama14@gmail.com")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.environ.get("SMTP_FROM_EMAIL", "ravinderkama14@gmail.com")
    SMTP_FROM_NAME: str = os.environ.get("SMTP_FROM_NAME", "Interview Coach AI")
    EMAIL_API_KEY: str = os.environ.get("EMAIL_API_KEY", os.environ.get("RESEND_API_KEY", ""))
    RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", os.environ.get("EMAIL_API_KEY", ""))

    # Frontend URL (for redirects after OAuth)
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def google_oauth_configured(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)

settings = Settings()
