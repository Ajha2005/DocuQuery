from app.services.chunking_service import chunk_text


def test_chunk_text_single_page_no_overlap_needed():
    """A page shorter than chunk_size should produce exactly one chunk."""
    pages = [{"page_number": 1, "text": "word " * 10}]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 0


def test_chunk_text_creates_overlap():
    """Consecutive chunks should share `overlap` words at the boundary."""
    pages = [{"page_number": 1, "text": " ".join(f"w{i}" for i in range(100))}]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)

    assert len(chunks) >= 2

    first_words = chunks[0]["content"].split()
    second_words = chunks[1]["content"].split()

    # Last 10 words of chunk 0 should equal first 10 words of chunk 1
    assert first_words[-10:] == second_words[:10]


def test_chunk_text_preserves_page_numbers_across_pages():
    """Chunks from page 2 should never be tagged with page 1's number."""
    pages = [
        {"page_number": 1, "text": "alpha " * 5},
        {"page_number": 2, "text": "beta " * 5},
    ]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)

    page_numbers = {c["page_number"] for c in chunks}
    assert page_numbers == {1, 2}


def test_chunk_text_skips_empty_pages():
    """Blank pages should not produce empty chunks."""
    pages = [
        {"page_number": 1, "text": ""},
        {"page_number": 2, "text": "real content here"},
    ]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 2


def test_chunk_index_increments_globally_across_pages():
    """chunk_index should keep counting up across page boundaries, not reset."""
    pages = [
        {"page_number": 1, "text": "alpha " * 60},
        {"page_number": 2, "text": "beta " * 60},
    ]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)

    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))
