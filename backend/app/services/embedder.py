from openai import OpenAI
from app.config import settings

_client = OpenAI(api_key=settings.openai_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """batch embedding, 100 items per batch to, avoid the batch large."""
    if not texts:
        return []
    out: list[list[float]] = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = _client.embeddings.create(
            model=settings.openai_embedding_model,
            input=batch,
        )
        out.extend([d.embedding for d in resp.data])
    return out