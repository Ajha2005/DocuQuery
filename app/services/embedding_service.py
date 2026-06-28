from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Loads the sentence-transformers model once and caches it.

    Why lru_cache: loading this model from disk takes a few seconds.
    Without caching, every embedding call would reload it from scratch.
    With maxsize=1, the model is loaded exactly once per process,
    then reused for every request.
    """
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """
    Generates a single embedding vector for one piece of text.
    Returns a plain Python list of 384 floats (matches Chunk.embedding column).
    """
    model = get_embedding_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for multiple texts in a single batch.

    Why batching matters: encoding 100 chunks one at a time means
    100 separate forward passes through the model. Batching lets the
    model process them together, which is significantly faster on
    both CPU and GPU.
    """
    model = get_embedding_model()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()
