import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.auth.dependencies import get_current_user
from backend.services import chat_service
from backend.services.export_service import format_chat_txt, format_chat_pdf, format_share_payload

router = APIRouter(prefix="/export", tags=["Export"])


def _get_chat_data(db: Session, chat_id: int, user_id: int):
    session = chat_service.get_chat_session(db, chat_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = chat_service.get_messages(db, chat_id)
    msg_list = [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in messages
    ]
    return session, msg_list


@router.get("/txt/{chat_id}")
def export_txt(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session, messages = _get_chat_data(db, chat_id, current_user.id)
    content = format_chat_txt(session.title, session.category, messages)
    filename = f"chat_{chat_id}_{session.title[:30].replace(' ', '_')}.txt"
    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/pdf/{chat_id}")
def export_pdf(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session, messages = _get_chat_data(db, chat_id, current_user.id)
    pdf_bytes = format_chat_pdf(session.title, session.category, messages)
    filename = f"chat_{chat_id}_{session.title[:30].replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/share/{chat_id}")
def share_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session, messages = _get_chat_data(db, chat_id, current_user.id)
    payload = format_share_payload(session.title, session.category, messages)
    return {
        "share_data": payload,
        "share_json": json.dumps(payload, indent=2),
    }
