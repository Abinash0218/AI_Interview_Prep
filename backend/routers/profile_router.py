from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.auth.password import hash_password, verify_password
from backend.auth.dependencies import get_current_user
from backend.services.chat_service import get_or_create_settings
from backend.schemas.profile import ProfileUpdateRequest, ChangePasswordRequest, SettingsUpdateRequest

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = get_or_create_settings(db, current_user.id)
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "profile_picture": current_user.profile_picture,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat(),
        "settings": {
            "preferred_theme": settings.preferred_theme,
            "preferred_model": settings.preferred_model,
        },
    }


@router.put("")
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.full_name:
        current_user.full_name = request.full_name.strip()
    if request.profile_picture is not None:
        current_user.profile_picture = request.profile_picture
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated", "user": {"full_name": current_user.full_name, "profile_picture": current_user.profile_picture}}


@router.put("/password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.password_hash:
        raise HTTPException(status_code=400, detail="Google account users should set password via reset flow")
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.put("/settings")
def update_settings(
    request: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = get_or_create_settings(db, current_user.id)
    if request.preferred_theme and request.preferred_theme in ("light", "dark"):
        settings.preferred_theme = request.preferred_theme
    if request.preferred_model and request.preferred_model in ("gemini", "groq"):
        settings.preferred_model = request.preferred_model
    db.commit()
    return {"message": "Settings updated", "settings": {"preferred_theme": settings.preferred_theme, "preferred_model": settings.preferred_model}}
