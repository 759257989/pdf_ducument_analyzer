from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Document, get_db
from app.schemas import ChatRequest, ChatResponse, Citation
from app.services.llm import answer
from app.services.retriever import retrieve

router = APIRouter()

# chat with the documents
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not req.question.strip():
        raise HTTPException(400, "question cannot be empty")
    if not req.doc_ids:
        raise HTTPException(400, "please select at least one document")

    docs = db.query(Document).filter(Document.id.in_(req.doc_ids)).all()
    if not docs:
        raise HTTPException(404, "cannot find these documents")
    name_map = {d.id: d.filename for d in docs}

    hits = retrieve(req.question, req.doc_ids, top_k=settings.retrieval_top_k)
    if not hits:
        return ChatResponse(
            answer="Sorry, I could not find relevant information in the uploaded document.",
            citations=[],
        )

    text = answer(req.question, hits, req.history)

    citations = [
        Citation(
            doc_id=h["doc_id"],
            filename=name_map.get(h["doc_id"], "?"),
            page_number=h["page_number"],
            snippet=h["text"][:200],
        )
        for h in hits
    ]
    return ChatResponse(answer=text, citations=citations)