from typing import Optional, List
from pydantic import BaseModel, field_validator


VALID_CATEGORIES = [
    "technical_interview",
    "coding_assessment",
    "hr_interview",
    "non_technical_skills",
]


class ChatRequest(BaseModel):
    message: str
    category: str
    chat_id: Optional[int] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {VALID_CATEGORIES}")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message too long (max 10000 characters)")
        return v


class RenameChatRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title too long")
        return v


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: str


class ChatSessionResponse(BaseModel):
    id: int
    category: str
    title: str
    created_at: str
    updated_at: str
    messages: Optional[List[MessageResponse]] = None
