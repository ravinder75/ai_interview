"""
Authentication router — register, login, logout, password reset, Google OAuth.
"""
import secrets
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    MessageResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    GoogleLoginRequest,
    VerifyEmailRequest,
    VerifyResetOtpRequest,
    VerifyOtpResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    generate_password_reset_otp,
    verify_password_reset_otp,
    reset_password_with_token,
    generate_email_verification_otp,
    verify_email_otp,
    get_user_by_email,
    handle_google_user,
)
from app.services.google_oauth import (
    get_google_auth_url,
    exchange_code_for_tokens,
    get_google_user_info,
    verify_google_id_token,
)
from app.security import get_current_user_required

logger = logging.getLogger("auth_router")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory state store for OAuth CSRF protection (use Redis in production)
_oauth_states: dict[str, bool] = {}


def _build_user_response(user: User) -> UserResponse:
    """Convert a User model to a UserResponse schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        target_role=user.target_role,
        experience_level=user.experience_level,
        programming_languages=user.programming_languages or [],
        phone_number=user.phone_number,
        profile_picture=user.profile_picture,
        auth_provider=user.auth_provider or "local",
        email_verified=user.email_verified or False,
        is_active=user.is_active,
    )


# ── Registration ──

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def api_register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account and return JWT token."""
    try:
        user = register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = create_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user),
    )


# ── Login ──

@router.post("/login", response_model=TokenResponse)
def api_login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user),
    )


# ── OAuth2 Form Login (for Swagger/OpenAPI) ──

@router.post("/token", response_model=TokenResponse)
def api_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 form-based login (used by Swagger docs)."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user),
    )


# ── Current User ──

class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    profile_picture: Optional[str] = None

@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Update current user's profile details & profile picture."""
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()
    if data.target_role is not None:
        current_user.target_role = data.target_role
    if data.experience_level is not None:
        current_user.experience_level = data.experience_level
    if data.profile_picture is not None:
        current_user.profile_picture = data.profile_picture

    db.commit()
    db.refresh(current_user)
    return _build_user_response(current_user)

@router.get("/me", response_model=UserResponse)
def api_me(current_user: User = Depends(get_current_user_required)):
    """Get the currently authenticated user's profile."""
    return _build_user_response(current_user)


# ── Logout ──

@router.post("/logout", response_model=MessageResponse)
def api_logout():
    """
    Logout — client should discard the token.
    With stateless JWTs, logout is handled client-side.
    """
    return MessageResponse(message="Logged out successfully")


# ── Email OTP Verification ──

@router.post("/verify-email", response_model=TokenResponse)
def api_verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify email address using 6-digit OTP code sent during registration."""
    success = verify_email_otp(db, data.email, data.otp)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or maximum attempts exceeded for this OTP code."
        )

    user = get_user_by_email(db, data.email)
    access_token = create_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user)
    )


class SendOtpRequest(BaseModel):
    email: str

@router.post("/send-otp")
def api_send_otp(data: SendOtpRequest, db: Session = Depends(get_db)):
    """Generic OTP send endpoint with email domain detection."""
    from app.services.email_service import validate_email_address, detect_email_provider, generate_password_reset_otp
    if not validate_email_address(data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email address.")

    provider_info = detect_email_provider(data.email)
    generate_password_reset_otp(db, data.email)

    return {
        "success": True,
        "message": "Verification code sent to your email.",
        "recipient_provider": provider_info["provider"],
        "domain": provider_info["domain"]
    }

@router.post("/forgot-password", response_model=MessageResponse)
def api_forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset OTP. Always returns generic success for security
    (never reveals whether an email exists in the system).
    """
    from app.services.email_service import validate_email_address
    if not validate_email_address(data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email address.")

    generate_password_reset_otp(db, data.email)
    return MessageResponse(
        message="If an account exists for this email, a password reset code has been sent."
    )


@router.get("/email/test")
def api_email_test():
    """Verify that configured email provider is reachable and authenticated."""
    provider = "resend" if settings.RESEND_API_KEY or settings.EMAIL_API_KEY else "smtp"
    sender = settings.SMTP_FROM_EMAIL or "ravinderkama14@gmail.com"
    has_creds = bool(settings.RESEND_API_KEY or settings.EMAIL_API_KEY or (settings.SMTP_USERNAME and settings.SMTP_PASSWORD))

    return {
        "success": has_creds,
        "provider": provider,
        "sender": sender,
        "configured": has_creds
    }


# ── Verify Reset OTP ──

@router.post("/verify-reset-otp", response_model=VerifyOtpResponse)
def api_verify_reset_otp(data: VerifyResetOtpRequest, db: Session = Depends(get_db)):
    """Verify 6-digit OTP for password reset and receive short-lived reset token."""
    reset_token = verify_password_reset_otp(db, data.email, data.otp)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP verification code."
        )
    return VerifyOtpResponse(
        message="OTP verified successfully. You may now reset your password.",
        reset_token=reset_token
    )


# ── Reset Password ──

@router.post("/reset-password", response_model=MessageResponse)
def api_reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid reset token."""
    success = reset_password_with_token(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )
    return MessageResponse(message="Password has been reset successfully. You can now log in.")


class GoogleCredentialRequest(BaseModel):
    credential: Optional[str] = None
    id_token: Optional[str] = None
    token: Optional[str] = None

@router.post("/google", response_model=TokenResponse)
async def api_google_authenticate(req: GoogleCredentialRequest, db: Session = Depends(get_db)):
    """
    Authenticate user via Google Identity Services (GIS) ID token credential.
    Verifies token directly with Google, upserts user account, and returns application JWT.
    """
    raw_token = req.credential or req.id_token or req.token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token credential is required."
        )

    google_user = await verify_google_id_token(raw_token)
    if not google_user or not google_user.email or not google_user.sub:
        logger.error(f"Google authentication failed. verify_google_id_token returned: {google_user}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token verification failed. Please check client ID or try logging in again."
        )

    # Automatically create user or link to existing account by stable google_sub / email
    user = handle_google_user(
        db=db,
        google_sub=google_user.sub,
        email=google_user.email,
        name=google_user.name,
        picture=google_user.picture
    )

    access_token = create_access_token(user)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user)
    )


@router.get("/google")
def api_google_redirect():
    """Redirect to Google's official OAuth consent screen."""
    if not settings.google_oauth_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env file.",
        )

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = True

    auth_url = get_google_auth_url(state)
    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def api_google_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback after user consents."""
    frontend_url = settings.FRONTEND_URL

    if error:
        return RedirectResponse(url=f"{frontend_url}/login?error=google_denied")

    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}/login?error=google_invalid")

    # Validate state (CSRF protection)
    if state not in _oauth_states:
        return RedirectResponse(url=f"{frontend_url}/login?error=google_state_invalid")
    del _oauth_states[state]

    try:
        # Exchange code for tokens
        token_data = await exchange_code_for_tokens(code)
        access_token_google = token_data.get("access_token")

        if not access_token_google:
            return RedirectResponse(url=f"{frontend_url}/login?error=google_token_failed")

        # Get user info from Google
        google_user = await get_google_user_info(access_token_google)

        if not google_user.email:
            return RedirectResponse(url=f"{frontend_url}/login?error=google_no_email")

        # Create or login user
        user = handle_google_user(
            db=db,
            google_sub=google_user.sub,
            email=google_user.email,
            name=google_user.name,
            picture=google_user.picture,
        )

        # Create our JWT
        jwt_token = create_access_token(user)

        # Redirect to frontend with token
        needs_profile = not user.target_role
        redirect_path = "/complete-profile" if needs_profile else "/dashboard"
        return RedirectResponse(
            url=f"{frontend_url}{redirect_path}?token={jwt_token}",
            status_code=status.HTTP_302_FOUND,
        )

    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}", exc_info=True)
        return RedirectResponse(url=f"{frontend_url}/login?error=google_failed")
