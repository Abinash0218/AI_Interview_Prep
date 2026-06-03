from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.auth.dependencies import get_current_user
from backend.schemas.chat import ChatRequest, RenameChatRequest
from backend.services import chat_service
from backend.prompts import CATEGORY_LABELS

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = chat_service.process_chat_message(
            db=db,
            user_id=current_user.id,
            category=request.category,
            user_message=request.message,
            chat_id=request.chat_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/history")
def get_history(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = chat_service.get_chat_history(db, current_user.id, search)
    grouped = {}
    for s in sessions:
        label = CATEGORY_LABELS.get(s.category, s.category)
        if label not in grouped:
            grouped[label] = []
        grouped[label].append({
            "id": s.id,
            "category": s.category,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        })
    return {"chats": grouped, "total": len(sessions)}


@router.get("/{chat_id}")
def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = chat_service.get_chat_session(db, chat_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = chat_service.get_messages(db, chat_id)
    return {
        "id": session.id,
        "category": session.category,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in messages
        ],
    }


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not chat_service.delete_chat(db, chat_id, current_user.id):
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted"}


@router.put("/{chat_id}/rename")
def rename_chat(
    chat_id: int,
    request: RenameChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = chat_service.rename_chat(db, chat_id, current_user.id, request.title)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat renamed", "title": session.title}
