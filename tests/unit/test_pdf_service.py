import pytest

from app.services.pdf_service import extract_text_by_page, get_page_count, PDFExtractionError

SAMPLE_PDF_PATH = "tests/fixtures/sample.pdf"


def test_get_page_count_returns_correct_count():
    count = get_page_count(SAMPLE_PDF_PATH)
    assert count == 1


def test_extract_text_by_page_returns_list_of_dicts():
    pages = extract_text_by_page(SAMPLE_PDF_PATH)
    assert len(pages) == 1
    assert "page_number" in pages[0]
    assert "text" in pages[0]


def test_extract_text_by_page_uses_1_indexed_pages():
    pages = extract_text_by_page(SAMPLE_PDF_PATH)
    assert pages[0]["page_number"] == 1  # not 0


def test_extract_text_contains_expected_content():
    pages = extract_text_by_page(SAMPLE_PDF_PATH)
    assert "Dummy" in pages[0]["text"]


def test_extract_text_raises_on_invalid_file():
    with pytest.raises(PDFExtractionError):
        extract_text_by_page("tests/fixtures/does_not_exist.pdf")
