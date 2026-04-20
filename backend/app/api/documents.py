from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
import hashlib
from app.auth import current_user
from app.config import settings
from app.db import Document, SessionLocal, User, get_db
from app.schemas import DocumentOut
from app.services.chunker import chunk_pages
from app.services.embedder import embed_texts
from app.services.pdf_parser import extract_pages
from app.vector_store import add_chunks, delete_doc

router = APIRouter()


def _process(doc_id: str, pdf_path: Path, user_id: str):
    """background task: flow: parse → chunk → embed → write Chroma → update status."""
    db = SessionLocal()
    try:
        pages = extract_pages(pdf_path)
        chunks = chunk_pages(
            doc_id, pages,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        if chunks:
            embeddings = embed_texts([c.text for c in chunks])
            add_chunks(chunks, embeddings, user_id=user_id)

        doc = db.get(Document, doc_id)
        doc.page_count = len(pages)
        doc.chunk_count = len(chunks)
        doc.status = "ready"
        db.commit()
    except Exception as e:
        doc = db.get(Document, doc_id)
        if doc:
            doc.status = "failed"
            doc.error = str(e)[:500]
            db.commit()
    finally:
        db.close()

# upload a pdf file
@router.post("/documents", response_model=DocumentOut)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "only accept pdf files")

    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()

    # check for duplicates
    existing = db.query(Document).filter(
        Document.user_id == user.id,
        Document.content_hash == content_hash,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "This pdf has been uploaded",
                "existing_doc_id": existing.id,
                "existing_filename": existing.filename,
            },
        )

    doc_id = uuid4().hex
    pdf_path = settings.uploads_dir / f"{doc_id}.pdf"
    with pdf_path.open("wb") as f:
        f.write(content)

    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=file.filename,
        content_hash=content_hash,   # save the content hash
        status="processing",
    )
    db.add(doc); db.commit(); db.refresh(doc)
    background.add_task(_process, doc_id, pdf_path, user.id)
    return doc

# list all documents
@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return (
        db.query(Document)
        .filter(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


# delete a document
@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    doc = db.get(Document, doc_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(404, "Document not found")
    delete_doc(doc_id)
    (settings.uploads_dir / f"{doc_id}.pdf").unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
    return {"ok": True}