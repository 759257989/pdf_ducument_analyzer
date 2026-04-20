from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str
    error: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class Citation(BaseModel):
    doc_id: str
    filename: str
    page_number: int
    snippet: str


class ChatRequest(BaseModel):
    question: str
    doc_ids: list[str]
    history: list[dict] = []  # [{role: 'user'|'assistant', content: '...'}]


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[Citation] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class ChatRequest(BaseModel):
    question: str
    doc_ids: list[str]
    conversation_id: str | None = None   # None = new conversation


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conversation_id: str                  # tell frontend the id when new conversation