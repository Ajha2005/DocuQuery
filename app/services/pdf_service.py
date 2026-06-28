import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be opened or parsed."""
    pass


def extract_text_by_page(file_path: str) -> list[dict]:
    """
    Extracts text from a PDF, page by page.

    Returns a list of dicts like:
        [{"page_number": 1, "text": "..."}, {"page_number": 2, "text": "..."}]

    Page numbers are 1-indexed because that's what humans expect
    when citing a source ("see page 3"), not 0-indexed like PyMuPDF
    internally uses.
    """
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise PDFExtractionError(f"Could not open PDF: {e}") from e

    pages = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text()
        pages.append({
            "page_number": page_index + 1,
            "text": text.strip(),
        })

    doc.close()
    return pages


def get_page_count(file_path: str) -> int:
    """Returns total page count without extracting text."""
    try:
        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        raise PDFExtractionError(f"Could not open PDF: {e}") from e
