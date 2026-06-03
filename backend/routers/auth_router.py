import logging
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.models.user_settings import UserSettings
from backend.models.password_reset import PasswordResetToken
from backend.auth.password import hash_password, verify_password
from backend.auth.jwt_handler import create_access_token
from backend.auth.dependencies import get_current_user
from backend.oauth.google import verify_google_token, exchange_google_code
from backend.schemas.auth import (
    SignUpRequest,
    LoginRequest,
    GoogleLoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse,
)
from backend.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("auth")
settings = get_settings()


def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=request.full_name,
        email=request.email.lower(),
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(UserSettings(user_id=user.id))
    db.commit()

    token = create_access_token(user.id, user.email)
    logger.info("User signed up: %s", user.email)
    return AuthResponse(access_token=token, user=_user_to_dict(user))


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.email)
    logger.info("User logged in: %s", user.email)
    return AuthResponse(access_token=token, user=_user_to_dict(user))


@router.post("/google-login", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    google_info = None
    if request.id_token:
        google_info = await verify_google_token(request.id_token)
    elif request.code:
        google_info = await exchange_google_code(request.code, request.redirect_uri)

    if not google_info:
        raise HTTPException(status_code=401, detail="Invalid Google credentials")

    user = db.query(User).filter(User.google_id == google_info["google_id"]).first()
    if not user:
        user = db.query(User).filter(User.email == google_info["email"].lower()).first()
        if user:
            user.google_id = google_info["google_id"]
            if google_info.get("profile_picture"):
                user.profile_picture = google_info["profile_picture"]
        else:
            user = User(
                full_name=google_info["full_name"],
                email=google_info["email"].lower(),
                google_id=google_info["google_id"],
                profile_picture=google_info.get("profile_picture"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(UserSettings(user_id=user.id))

    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.email)
    logger.info("Google login: %s", user.email)
    return AuthResponse(access_token=token, user=_user_to_dict(user))


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user:
        return {"message": "If the email exists, a reset link has been sent."}

    token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(reset)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}?reset_token={token}"
    logger.info("Password reset requested for %s. Token link: %s", user.email, reset_link)
    return {
        "message": "If the email exists, a reset link has been sent.",
        "reset_token": token,
        "reset_link": reset_link,
    }


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(request.new_password)
    reset.used = True
    db.commit()
    logger.info("Password reset completed for user id %s", user.id)
    return {"message": "Password reset successful"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    logger.info("User logged out: %s", current_user.email)
    return {"message": "Logged out successfully"}
