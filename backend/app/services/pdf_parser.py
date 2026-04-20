import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class Page:
    page_number: int   # 1-indexed, the same as the page number in the pdf reader
    text: str


def extract_pages(pdf_path: Path) -> list[Page]:
    """from pdf extract each page text, keep the page number."""
    pages: list[Page] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            # "text" mode output the text in the reading order, for the chinese multi-column layout
            raw = page.get_text("text")
            cleaned = _clean(raw)
            if cleaned.strip():
                pages.append(Page(page_number=i, text=cleaned))
    return pages


def _clean(text: str) -> str:
    lines = [line.rstrip() for line in text.split("\n")]
    result = "\n".join(lines)
    # if there are more than two empty lines, compress them to two used to remove the noise)
    return re.sub(r"\n{3,}", "\n\n", result)