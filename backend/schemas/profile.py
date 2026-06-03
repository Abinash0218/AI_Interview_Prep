from typing import Optional
from pydantic import BaseModel, EmailStr


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class SettingsUpdateRequest(BaseModel):
    preferred_theme: Optional[str] = None
    preferred_model: Optional[str] = None
