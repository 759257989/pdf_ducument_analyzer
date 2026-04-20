import chromadb

from app.config import settings
from app.services.chunker import Chunk

_client = chromadb.PersistentClient(path=str(settings.chroma_dir))
_collection = _client.get_or_create_collection(
    name="chunks",
    metadata={"hnsw:space": "cosine"},
)


def add_chunks(chunks: list[Chunk], embeddings: list[list[float]], user_id: str) -> None:
    if not chunks:
        return
    _collection.add(
        ids=[f"{c.doc_id}:{c.chunk_index}" for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "doc_id": c.doc_id,
                "user_id": user_id,
                "page_number": c.page_number,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ],
    )


def query(
    query_embedding: list[float],
    user_id: str,
    doc_ids: list[str],
    top_k: int = 6,
) -> list[dict]:
    where = {
        "$and": [
            {"user_id": user_id},
            {"doc_id": {"$in": doc_ids}},
        ]
    }
    res = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )
    hits = []
    for i, doc in enumerate(res["documents"][0]):
        hits.append({
            "text": doc,
            "doc_id": res["metadatas"][0][i]["doc_id"],
            "page_number": res["metadatas"][0][i]["page_number"],
            "distance": res["distances"][0][i],
        })
    return hits


def delete_doc(doc_id: str) -> None:
    _collection.delete(where={"doc_id": doc_id})