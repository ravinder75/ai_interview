"""
Core authentication service — registration, login, JWT, password reset.
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.models.email_verification import EmailVerificationToken
from app.services.password_service import hash_password, verify_password
from app.schemas.auth import UserRegister

logger = logging.getLogger("auth_service")


# ── JWT ──

def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for the given user."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode = {
        "sub": user.email,
        "user_id": user.id,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# ── User Lookup ──

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find a user by normalized email."""
    return db.query(User).filter(User.email == email.strip().lower()).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_google_sub(db: Session, google_sub: str) -> Optional[User]:
    """Find a user by Google subject ID."""
    return db.query(User).filter(User.google_sub == google_sub).first()


# ── Registration ──

def register_user(db: Session, data: UserRegister) -> User:
    """
    Register a new local user. Raises ValueError for business rule violations.
    """
    email = data.email.strip().lower()

    # Check for duplicate
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("An account with this email already exists.")

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        full_name=data.name.strip(),
        auth_provider="local",
        target_role=data.target_role,
        experience_level=data.experience_level,
        programming_languages=data.programming_languages or [],
        phone_number=data.phone_number,
        location=data.location,
        email_verified=False,
        is_active=True,
        terms_accepted_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: id={user.id}")

    # Generate and send verification OTP
    generate_email_verification_otp(db, user)

    return user


# ── Login ──

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    Returns the User on success, None on failure.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.hashed_password:
        # Google-only account — no local password
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return user


# ── Google OAuth Account Handling ──

def handle_google_user(
    db: Session,
    google_sub: str,
    email: str,
    name: str,
    picture: Optional[str] = None,
) -> User:
    """
    Handle a user authenticated via Google OAuth.
    - If a user with this google_sub exists, log them in.
    - If a local user with this email exists, link the Google account.
    - Otherwise, create a new Google account.
    """
    email = email.strip().lower()

    # Check by Google subject ID first
    user = get_user_by_google_sub(db, google_sub)
    if user:
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        return user

    # Check if a local account with this email exists
    user = get_user_by_email(db, email)
    if user:
        # Link Google account to existing local account
        user.google_sub = google_sub
        if user.auth_provider in ["local", "email"]:
            user.auth_provider = "email_google"
        user.email_verified = True  # Google verified the email
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Linked Google account to existing user: id={user.id}")
        return user

    # Create new Google account
    user = User(
        email=email,
        full_name=name or "Google User",
        auth_provider="google",
        google_sub=google_sub,
        profile_picture=picture,
        email_verified=True,
        is_active=True,
        terms_accepted_at=datetime.now(timezone.utc),
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New Google user created: id={user.id}")
    return user


# ── Email OTP Verification ──

def generate_email_verification_otp(db: Session, user: User) -> str:
    """Generate a 6-digit OTP for email verification and send via email service."""
    otp = f"{secrets.randbelow(900000) + 100000}"  # 6-digit cryptographically secure random code
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    token = EmailVerificationToken(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0
    )
    db.add(token)
    db.commit()

    from app.services.email_service import send_email_verification_otp
    send_email_verification_otp(user.email, otp)
    logger.info(f"Generated email verification OTP for user_id={user.id}")
    return otp

def verify_email_otp(db: Session, email: str, otp: str) -> bool:
    """Verify 6-digit OTP for email verification."""
    user = get_user_by_email(db, email)
    if not user:
        return False

    otp_hash = hashlib.sha256(otp.strip().encode()).hexdigest()
    token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None)
    ).order_by(EmailVerificationToken.created_at.desc()).first()

    if not token:
        return False

    token.attempts += 1

    # Check attempt limit
    if token.attempts > 5:
        db.commit()
        return False

    # Check expiry
    now = datetime.now(timezone.utc)
    exp = token.expires_at.replace(tzinfo=timezone.utc) if token.expires_at.tzinfo is None else token.expires_at
    if now > exp:
        db.commit()
        return False

    if token.otp_hash != otp_hash:
        db.commit()
        return False

    # Success
    token.used_at = now
    user.email_verified = True
    db.commit()
    return True


# ── Password Reset OTP ──

def generate_password_reset_otp(db: Session, email: str) -> Optional[str]:
    """Generate a 6-digit OTP for password reset."""
    user = get_user_by_email(db, email)
    if not user:
        return None  # Caller will return generic message for security

    otp = f"{secrets.randbelow(900000) + 100000}"
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    reset = PasswordReset(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0
    )
    db.add(reset)
    db.commit()

    from app.services.email_service import send_password_reset_otp
    send_password_reset_otp(user.email, otp)
    logger.info(f"Generated password reset OTP for user_id={user.id}")
    return otp

def verify_password_reset_otp(db: Session, email: str, otp: str) -> Optional[str]:
    """Verify 6-digit OTP and issue a short-lived reset token on success."""
    user = get_user_by_email(db, email)
    if not user:
        return None

    otp_hash = hashlib.sha256(otp.strip().encode()).hexdigest()
    reset = db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id,
        PasswordReset.used_at.is_(None)
    ).order_by(PasswordReset.created_at.desc()).first()

    if not reset:
        return None

    reset.attempts += 1

    if reset.attempts > 5:
        db.commit()
        return None

    now = datetime.now(timezone.utc)
    exp = reset.expires_at.replace(tzinfo=timezone.utc) if reset.expires_at.tzinfo is None else reset.expires_at
    if now > exp:
        db.commit()
        return None

    if reset.otp_hash != otp_hash:
        db.commit()
        return None

    # Success: issue reset token
    raw_token = secrets.token_urlsafe(32)
    reset.token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset.verified_at = now
    db.commit()
    return raw_token

def reset_password_with_token(db: Session, raw_token: str, new_password: str) -> bool:
    """Reset password using verified reset token."""
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    reset = db.query(PasswordReset).filter(
        PasswordReset.token_hash == token_hash,
        PasswordReset.used_at.is_(None),
        PasswordReset.verified_at.isnot(None)
    ).first()

    if not reset:
        return False

    user = get_user_by_id(db, reset.user_id)
    if not user:
        return False

    user.hashed_password = hash_password(new_password)
    reset.used_at = datetime.now(timezone.utc)
    db.commit()
    logger.info(f"Password reset completed for user_id={user.id}")
    return True
