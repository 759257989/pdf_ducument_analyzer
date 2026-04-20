from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Document, SessionLocal, get_db
from app.schemas import DocumentOut
from app.services.chunker import chunk_pages
from app.services.embedder import embed_texts
from app.services.pdf_parser import extract_pages
from app.vector_store import add_chunks, delete_doc

router = APIRouter()


def _process(doc_id: str, pdf_path: Path):
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
            add_chunks(chunks, embeddings)

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
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "only accept pdf files")

    doc_id = uuid4().hex
    pdf_path = settings.uploads_dir / f"{doc_id}.pdf"
    with pdf_path.open("wb") as f:
        f.write(await file.read())

    doc = Document(id=doc_id, filename=file.filename, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background.add_task(_process, doc_id, pdf_path)
    return doc


# list all documents
@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


# delete a document
@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "document not found")
    delete_doc(doc_id)
    (settings.uploads_dir / f"{doc_id}.pdf").unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
    return {"ok": True}