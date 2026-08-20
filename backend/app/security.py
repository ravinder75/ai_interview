"""
Security dependencies for FastAPI route protection.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Decode JWT and return the user, or None if not authenticated.
    """
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    user = get_user_by_email(db, email)
    if user and not user.is_active:
        return None
    return user


async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Require authentication. Raises 401 if not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
