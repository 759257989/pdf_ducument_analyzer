import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import current_user
from app.db import Conversation, Message, User, get_db
from app.schemas import Citation, ConversationDetail, ConversationOut, MessageOut

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/conversations/{conv_id}", response_model=ConversationDetail)
def get_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "Conversation not found")
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
        .all()
    )
    messages_out = []
    for m in msgs:
        citations = []
        if m.citations_json:
            citations = [Citation(**c) for c in json.loads(m.citations_json)]
        messages_out.append(MessageOut(
            id=m.id, role=m.role, content=m.content,
            citations=citations, created_at=m.created_at,
        ))
    return ConversationDetail(
        id=conv.id, title=conv.title, created_at=conv.created_at,
        messages=messages_out,
    )


@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "Conversation not found")
    db.query(Message).filter(Message.conversation_id == conv_id).delete()
    db.delete(conv); db.commit()
    return {"ok": True}