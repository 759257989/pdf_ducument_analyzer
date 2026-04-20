from dataclasses import dataclass
from app.services.pdf_parser import Page

"""
chunk_size=600 中文约 300-400 字，实测效果好的默认值
发现答案检索不到 → 加大 chunk_size 或 top_k
发现答案夹了无关内容 → 减小 chunk_size
"""
@dataclass
class Chunk:
    doc_id: str
    chunk_index: int
    page_number: int  # the first page of the chunk
    text: str


def chunk_pages(
    doc_id: str,
    pages: list[Page],
    chunk_size: int = 600,
    overlap: int = 100,
) -> list[Chunk]:
    """split the pages into chunks, keep the overlap."""
    chunks: list[Chunk] = []
    buffer = ""
    buffer_start_page = 1
    idx = 0

    for page in pages:
        paragraphs = [p for p in page.text.split("\n\n") if p.strip()]
        for para in paragraphs:
            if not buffer:
                buffer_start_page = page.page_number
            # if the current buffer is too long, split it into a chunk
            if buffer and len(buffer) + len(para) + 2 > chunk_size:
                chunks.append(Chunk(
                    doc_id=doc_id, chunk_index=idx,
                    page_number=buffer_start_page, text=buffer.strip(),
                ))
                idx += 1
                # keep the overlap to the next chunk
                buffer = buffer[-overlap:] + "\n\n" + para
                buffer_start_page = page.page_number
            else:
                buffer += ("\n\n" if buffer else "") + para

    if buffer.strip():
        chunks.append(Chunk(
            doc_id=doc_id, chunk_index=idx,
            page_number=buffer_start_page, text=buffer.strip(),
        ))

    return chunks
