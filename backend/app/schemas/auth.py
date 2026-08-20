import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List


# ── Registration ──

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Full name")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    target_role: str = Field(..., min_length=1, max_length=100)
    experience_level: str = Field(..., min_length=1, max_length=50)
    programming_languages: Optional[List[str]] = Field(default_factory=list)
    terms_accepted: bool = Field(..., description="Must accept terms")

    # Optional fields
    phone_number: Optional[str] = Field(None, max_length=30)
    location: Optional[str] = Field(None, max_length=200)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name is required")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", v):
            errors.append("Password must contain at least one special character")
        if errors:
            raise ValueError("; ".join(errors))
        return v

    @field_validator("terms_accepted")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must accept the Terms and Privacy Policy")
        return v

    @field_validator("experience_level")
    @classmethod
    def validate_experience(cls, v: str) -> str:
        valid = [
            "Fresher", "Student", "Intern",
            "0-1 Years", "1-3 Years", "3-5 Years",
            "5-8 Years", "8+ Years"
        ]
        if v not in valid:
            raise ValueError(f"Experience level must be one of: {', '.join(valid)}")
        return v


# ── Login ──

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


# ── Forgot / Reset Password ──

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", v):
            errors.append("Password must contain at least one special character")
        if errors:
            raise ValueError("; ".join(errors))
        return v


# ── Google OAuth ──

class GoogleLoginRequest(BaseModel):
    """Legacy compatibility — not used in new OAuth flow"""
    google_token: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


# ── Responses ──

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    programming_languages: Optional[List[str]] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    auth_provider: str = "local"
    email_verified: bool = False
    is_active: bool = True

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

class VerifyResetOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

class VerifyOtpResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None


# Keep backward compatibility
Token = TokenResponse
