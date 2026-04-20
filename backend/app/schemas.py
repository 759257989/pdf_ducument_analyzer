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