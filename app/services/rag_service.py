from groq import Groq
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chunk import Chunk
from app.services.embedding_service import embed_text

TOP_K = 4  # how many chunks to retrieve as context
SNIPPET_LENGTH = 150  # characters shown in citation snippet

_groq_client = Groq(api_key=settings.GROQ_API_KEY)


def retrieve_relevant_chunks(db: Session, document_id: int, question: str, top_k: int = TOP_K) -> list[Chunk]:
    """
    Embeds the question and finds the top_k most similar chunks
    belonging to a specific document, using pgvector cosine distance.

    Why filter by document_id: queries are scoped to one document at
    a time (per the API design: /documents/{id}/query). Without this
    filter, a question about Document A could retrieve chunks from
    Document B — wrong answers with confident-sounding citations.
    """
    query_vector = embed_text(question)

    stmt = (
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.embedding.cosine_distance(query_vector))
        .limit(top_k)
    )
    return list(db.execute(stmt).scalars().all())


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """
    Builds a prompt that grounds the model's answer in retrieved context
    and explicitly instructs it not to hallucinate beyond that context.
    """
    context_blocks = []
    for chunk in chunks:
        context_blocks.append(
            f"[Page {chunk.page_number}] {chunk.content}"
        )
    context_text = "\n\n".join(context_blocks)

    return f"""You are answering questions based ONLY on the provided document excerpts below.
If the answer is not contained in the excerpts, say you don't have enough information to answer.
Do not use outside knowledge.

Document excerpts:
{context_text}

Question: {question}

Answer:"""


def generate_answer(prompt: str) -> str:
    """Calls Groq's chat completion API with the grounded prompt."""
    response = _groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # low temperature: we want grounded, consistent answers, not creativity
    )
    return response.choices[0].message.content


def answer_question(db: Session, document_id: int, question: str) -> dict:
    """
    Full RAG pipeline: retrieve -> build prompt -> generate -> format citations.
    """
    chunks = retrieve_relevant_chunks(db, document_id, question)

    if not chunks:
        return {
            "answer": "I don't have enough information to answer that — no relevant content was found in this document.",
            "sources": [],
        }

    prompt = build_prompt(question, chunks)
    answer = generate_answer(prompt)

    sources = [
        {
            "chunk_id": chunk.id,
            "page_number": chunk.page_number,
            "content_snippet": chunk.content[:SNIPPET_LENGTH] + ("..." if len(chunk.content) > SNIPPET_LENGTH else ""),
        }
        for chunk in chunks
    ]

    return {"answer": answer, "sources": sources}
