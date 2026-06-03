from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.models.chat_session import ChatSession
from backend.models.message import Message
from backend.models.user_settings import UserSettings
from backend.services.gemini_service import generate_response


def get_or_create_settings(db: Session, user_id: int) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def create_chat_session(db: Session, user_id: int, category: str, title: str = "New Chat") -> ChatSession:
    session = ChatSession(user_id=user_id, category=category, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_chat_session(db: Session, chat_id: int, user_id: int) -> Optional[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == chat_id, ChatSession.user_id == user_id)
        .first()
    )


def get_chat_history(db: Session, user_id: int, search: Optional[str] = None) -> List[ChatSession]:
    query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    if search:
        query = query.filter(
            or_(
                ChatSession.title.ilike(f"%{search}%"),
                ChatSession.category.ilike(f"%{search}%"),
            )
        )
    return query.order_by(ChatSession.updated_at.desc()).all()


def get_messages(db: Session, session_id: int) -> List[Message]:
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def rename_chat(db: Session, chat_id: int, user_id: int, title: str) -> Optional[ChatSession]:
    session = get_chat_session(db, chat_id, user_id)
    if session:
        session.title = title
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def delete_chat(db: Session, chat_id: int, user_id: int) -> bool:
    session = get_chat_session(db, chat_id, user_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False


def _generate_title_from_message(message: str) -> str:
    title = message.strip()[:50]
    if len(message.strip()) > 50:
        title += "..."
    return title or "New Chat"


def process_chat_message(
    db: Session,
    user_id: int,
    category: str,
    user_message: str,
    chat_id: Optional[int] = None,
) -> dict:
    settings = get_or_create_settings(db, user_id)

    if chat_id:
        session = get_chat_session(db, chat_id, user_id)
        if not session:
            raise ValueError("Chat session not found")
    else:
        title = _generate_title_from_message(user_message)
        session = create_chat_session(db, user_id, category, title)

    history_messages = get_messages(db, session.id)
    history = [{"role": m.role, "content": m.content} for m in history_messages]

    user_msg = Message(session_id=session.id, role="user", content=user_message)
    db.add(user_msg)
    db.commit()

    ai_response = generate_response(
        category=category,
        history=history,
        user_message=user_message,
        preferred_model=settings.preferred_model,
    )

    assistant_msg = Message(session_id=session.id, role="assistant", content=ai_response)
    db.add(assistant_msg)

    if session.title == "New Chat" or len(history_messages) == 0:
        session.title = _generate_title_from_message(user_message)

    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)

    return {
        "chat_id": session.id,
        "title": session.title,
        "category": session.category,
        "response": ai_response,
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in get_messages(db, session.id)
        ],
    }
