from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null for Google-only accounts
    full_name = Column(String(200), nullable=False)

    # Authentication provider
    auth_provider = Column(String(20), nullable=False, default="local")  # "local" or "google"
    google_sub = Column(String(255), unique=True, nullable=True, index=True)

    # Profile information
    target_role = Column(String(100), nullable=True)
    experience_level = Column(String(50), nullable=True)
    programming_languages = Column(JSON, nullable=True, default=list)
    phone_number = Column(String(30), nullable=True)
    location = Column(String(200), nullable=True)
    profile_picture = Column(Text, nullable=True)  # Base64 or avatar URL

    # Account status
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

