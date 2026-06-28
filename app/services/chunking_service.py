def chunk_text(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    Splits page-level text into overlapping chunks for embedding.

    Args:
        pages: output of pdf_service.extract_text_by_page()
        chunk_size: target chunk size in words
        overlap: number of words repeated between consecutive chunks

    Returns a list of dicts like:
        [{"content": "...", "page_number": 1, "chunk_index": 0}, ...]

    Why overlap matters: if a sentence describing something important
    gets cut in half at a chunk boundary, the model loses context.
    Overlapping words means the boundary "bleeds" into the next chunk,
    so meaning isn't lost at the edges.
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        words = page["text"].split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            content = " ".join(chunk_words)

            chunks.append({
                "content": content,
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
            })
            chunk_index += 1

            # Move start forward by (chunk_size - overlap), not chunk_size,
            # so the next chunk repeats the last `overlap` words.
            start += chunk_size - overlap

    return chunks
