import secrets
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User, UserRole
from app.auth.security import hash_password, verify_password, create_access_token, decode_token
from app.auth.google_oauth import (
    get_google_login_url,
    is_google_configured,
    REDIRECT_URI,
    FRONTEND_URL,
    SCOPES,
)

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def _get_token_from_header(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0].lower(), parts[1].strip()
    if scheme != "bearer" or not token:
        return None
    return token


def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    """Dependency: parse JWT and return user id. Raises 401 if invalid."""
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = decode_token(token)
        return int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return AuthResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "role": user.role.value if user.role else UserRole.USER.value,
        },
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.hashed_password:
        raise HTTPException(status_code=401, detail="Tài khoản đăng nhập bằng Google. Vui lòng dùng Đăng nhập với Google.")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return AuthResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "role": user.role.value if user.role else UserRole.USER.value,
        },
    )


@router.get("/me")
async def me(db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "role": user.role.value if user.role else UserRole.USER.value,
    }


# ----- Google OAuth -----

@router.get("/google/login")
async def google_login():
    """Return Google OAuth URL for frontend to redirect user."""
    if not is_google_configured():
        raise HTTPException(
            status_code=503,
            detail="Google login is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
        )
    state = secrets.token_urlsafe(32)
    url = get_google_login_url(state=state)
    return {"url": url, "state": state}


@router.get("/google/callback")
async def google_callback(code: str | None = None, state: str | None = None, error: str | None = None):
    """Exchange code for tokens, create/update user, redirect to frontend with JWT."""
    from app.auth.google_oauth import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=access_denied")
    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=missing_code")

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=server_config")

    from google_auth_oauthlib.flow import Flow
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        # Log chi tiết lỗi để debug nguyên nhân (redirect_uri_mismatch, invalid_grant, ...)
        import logging
        logging.exception("Google token exchange failed")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=token_exchange")

    credentials = flow.credentials
    id_token_jwt = credentials.id_token
    if not id_token_jwt:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_id_token")

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_jwt, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_id_token")

    google_id = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name") or idinfo.get("email", "").split("@")[0]
    avatar_url = idinfo.get("picture")
    refresh_token = getattr(credentials, "refresh_token", None) or ""

    if not email or not google_id:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_email")

    from app.database.db import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()
        if not user:
            # Placeholder hash so DB column can stay NOT NULL; user cannot login with password
            placeholder = hash_password(secrets.token_urlsafe(32))
            user = User(
                email=email,
                name=name,
                hashed_password=placeholder,
                google_id=google_id,
                google_refresh_token=refresh_token,
                avatar_url=avatar_url,
                role=UserRole.USER,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.google_id = google_id
            user.google_refresh_token = refresh_token
            if not user.name and name:
                user.name = name
            # Always keep latest avatar from Google if available
            if avatar_url:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)

        app_token = create_access_token(subject=str(user.id))
        redirect_url = f"{FRONTEND_URL}/auth/google/callback?token={app_token}"
        return RedirectResponse(url=redirect_url)
    finally:
        db.close()

