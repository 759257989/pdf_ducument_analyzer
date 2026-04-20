from app.services.chunker import chunk_pages
from app.services.pdf_parser import Page


def test_empty_pages():
    assert chunk_pages("d1", []) == []


def test_chunks_carry_page_number():
    pages = [
        Page(1, "First page content." * 80),
        Page(2, "Second page content." * 80),
    ]
    chunks = chunk_pages("d1", pages, chunk_size=200, overlap=30)
    assert len(chunks) > 0
    assert all(c.page_number in (1, 2) for c in chunks)
    # the first chunk comes from page 1
    assert chunks[0].page_number == 1


def test_chunks_respect_size():
    pages = [Page(1, "A" * 50 + "\n\n" + "B" * 50 + "\n\n" + "C" * 50)]
    chunks = chunk_pages("d1", pages, chunk_size=80, overlap=10)
    # force split, at least 2 chunks
    assert len(chunks) >= 2