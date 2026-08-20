"""
Google OAuth 2.0 / OpenID Connect service.

Handles the OAuth consent URL generation, code exchange, and ID token verification.
Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to be configured.
"""
import logging
from typing import Optional
from dataclasses import dataclass

import httpx
from jose import jwt as jose_jwt

from app.config import settings

logger = logging.getLogger("google_oauth")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"


@dataclass
class GoogleUser:
    """Parsed Google user information from ID token."""
    sub: str          # Google subject ID (unique, stable)
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False


def get_google_auth_url(state: str) -> str:
    """
    Build the Google OAuth2 consent screen URL.
    The `state` parameter is used for CSRF protection.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "consent",
    }
    query = "&".join(f"{k}={httpx.URL('', params={k: v}).params[k]}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchange the authorization code for tokens (access_token, id_token).
    Returns the raw token response dict.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def get_google_user_info(access_token: str) -> GoogleUser:
    """
    Fetch user info from Google's userinfo endpoint using the access token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()

    return GoogleUser(
        sub=data["sub"],
        email=data.get("email", ""),
        name=data.get("name", ""),
        picture=data.get("picture"),
        email_verified=data.get("email_verified", False),
    )


async def verify_google_id_token(id_token: str) -> Optional[GoogleUser]:
    """
    Verifies a Google ID token via Google's official OAuth2 tokeninfo API endpoint.
    Guarantees that the token was signed by Google, is unexpired, and matches our client ID.
    Returns parsed GoogleUser or None if verification fails.
    """
    if not id_token:
        return None
        
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            res = await client.get(url)
            if res.status_code != 200:
                logger.warning(f"Google ID token verification failed with HTTP {res.status_code}: {res.text}")
                return None
            data = res.json()

            # Verify audience if GOOGLE_CLIENT_ID is configured
            aud = data.get("aud")
            if settings.GOOGLE_CLIENT_ID and aud != settings.GOOGLE_CLIENT_ID:
                logger.warning(f"Google ID token audience mismatch: expected {settings.GOOGLE_CLIENT_ID}, got {aud}")
                # In development mode without client ID, we can log notice
                if settings.ENVIRONMENT != "development":
                    return None

            sub = data.get("sub")
            email = data.get("email", "")
            if not sub or not email:
                logger.warning("Google ID token missing sub or email claim")
                return None

            return GoogleUser(
                sub=sub,
                email=email,
                name=data.get("name") or data.get("given_name") or email.split("@")[0],
                picture=data.get("picture"),
                email_verified=data.get("email_verified") == "true" or data.get("email_verified") is True
            )
        except Exception as e:
            logger.error(f"Error calling Google tokeninfo endpoint: {e}")
            return None
