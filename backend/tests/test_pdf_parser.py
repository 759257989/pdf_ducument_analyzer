from pathlib import Path
import pytest

from app.services.pdf_parser import extract_pages

PDF = Path(__file__).parent.parent.parent / "腾讯2025年度报告.pdf"


@pytest.mark.skipif(not PDF.exists(), reason="Test PDF not found")
def test_extract_chinese_pdf_not_garbled():
    pages = extract_pages(PDF)
    assert len(pages) > 10
    all_text = "\n".join(p.text for p in pages)
    # must appear
    assert "腾讯" in all_text or "Tencent" in all_text
    # ? ratio is very low, means not replaced with question mark
    assert all_text.count("?") / max(len(all_text), 1) < 0.01


@pytest.mark.skipif(not PDF.exists(), reason="Test PDF not found")
def test_page_numbers_are_sequential():
    pages = extract_pages(PDF)
    nums = [p.page_number for p in pages]
    assert nums == sorted(nums)
    assert nums[0] >= 1