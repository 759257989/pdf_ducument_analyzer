from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Document, get_db
from app.schemas import ChatRequest, ChatResponse, Citation
from app.services.llm import answer
from app.services.retriever import retrieve
from app.auth import current_user
from app.db import User
import json
from uuid import uuid4

from app.db import Conversation, Message

router = APIRouter()

# chat with the documents
@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    if not req.doc_ids:
        raise HTTPException(400, "Please select at least one document")

    docs = db.query(Document).filter(
        Document.id.in_(req.doc_ids),
        Document.user_id == user.id,
    ).all()
    if len(docs) != len(req.doc_ids):
        raise HTTPException(403, "Some documents do not exist or you do not have access")
    name_map = {d.id: d.filename for d in docs}

    # find or create conversation
    if req.conversation_id:
        conv = db.get(Conversation, req.conversation_id)
        if not conv or conv.user_id != user.id:
            raise HTTPException(404, "Conversation not found")
    else:
        conv = Conversation(
            id=uuid4().hex, user_id=user.id,
            title=req.question[:50],
        )
        db.add(conv); db.commit(); db.refresh(conv)

    # history messages as LLM context
    history_msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in history_msgs]

    # save user message
    db.add(Message(
        id=uuid4().hex, conversation_id=conv.id,
        role="user", content=req.question,
    ))

    # retrieve + generate
    hits = retrieve(req.question, user.id, req.doc_ids, top_k=settings.retrieval_top_k)
    if not hits:
        text = "Sorry, I couldn't find any relevant information in your uploaded documents."
        citations = []
    else:
        text = answer(req.question, hits, history)
        citations = [
            Citation(
                doc_id=h["doc_id"],
                filename=name_map.get(h["doc_id"], "?"),
                page_number=h["page_number"],
                snippet=h["text"][:200],
            )
            for h in hits
        ]

    # save assistant message
    db.add(Message(
        id=uuid4().hex, conversation_id=conv.id,
        role="assistant", content=text,
        citations_json=json.dumps([c.model_dump() for c in citations]) if citations else None,
    ))
    db.commit()

    return ChatResponse(answer=text, citations=citations, conversation_id=conv.id)