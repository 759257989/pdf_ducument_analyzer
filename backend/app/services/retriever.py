from app.services.embedder import embed_texts
from app.vector_store import query as chroma_query


def retrieve(question: str, doc_ids: list[str], top_k: int = 6) -> list[dict]:
    # embed the question
    q_emb = embed_texts([question])[0]
    # query the chroma database
    return chroma_query(q_emb, doc_ids=doc_ids, top_k=top_k)