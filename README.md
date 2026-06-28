# 📄 DocuQuery

**Ask your PDFs questions in plain English — get grounded answers with page-level citations.**

DocuQuery is a Retrieval-Augmented Generation (RAG) application that lets you upload a PDF and query its contents using natural language. Answers are generated *only* from the document's actual content, never from the model's general knowledge — and every answer comes with a citation pointing back to the exact page it came from.

🔗 **Live demo:** [docuquery-production-9d5f.up.railway.app](https://docuquery-production-9d5f.up.railway.app)

> Upload a PDF, ask it a question, and watch it answer using only what's actually in the document — with proof.

---

## Why I built this

This is one half of a two-project portfolio designed to demonstrate end-to-end ML engineering across both structured and unstructured data:

- **[FinSight](https://github.com/Ajha2005/finsight)** — ML on structured data (transaction categorization, anomaly detection)
- **DocuQuery** (this project) — RAG on unstructured data (PDF retrieval + LLM generation)

Together they cover the two dominant data shapes in real-world ML systems, and the engineering discipline needed for each: schema design and feature engineering on one side, embeddings and retrieval pipelines on the other.

---

## Architecture
┌─────────────────────────────────────────────────────────┐

│                    CLIENT (browser / curl)                │

└──────────────────────┬──────────────────────────────────┘

│ HTTP

┌──────────────────────▼──────────────────────────────────┐

│                   FASTAPI APP                            │

│                                                          │

│   /documents        /documents/{id}/query                │

│   POST upload       POST ask question                    │

│   GET list          GET single document                 │

└──────┬──────────────────────────┬───────────────────────┘

│                          │

┌──────▼──────┐          ┌────────▼────────┐

│  PDF        │          │   RAG           │

│  SERVICE    │          │   SERVICE       │

│             │          │                 │

│ • extract   │          │ • embed query   │

│   text      │          │ • vector search │

│ • chunk     │          │ • build prompt  │

│ • embed     │          │ • call Groq     │

│ • store     │          │ • return answer │

└──────┬──────┘          │   + citations   │

│                 └────────┬────────┘

│                          │

┌──────▼──────────────────────────▼────────┐

│            PostgreSQL + pgvector          │

│                                          │

│  documents table    chunks table         │

│  ─────────────      ────────────         │

│  id                 id                   │

│  filename           document_id (FK)     │

│  upload_time        content              │

│  page_count         page_number          │

│  status             chunk_index          │

│                     embedding (vector)   │

│                     token_count          │

└──────────────────────────────────────────┘

│

┌────────▼────────┐

│   FREE STACK    │

│                 │

│ sentence-       │

│ transformers    │

│ (local embed)   │

│                 │

│ Groq API        │

│ (free chat)     │

└─────────────────┘

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | Async-friendly, automatic OpenAPI docs, dependency injection for clean DB sessions |
| Database | PostgreSQL + pgvector | Vector similarity search *inside* SQL — no separate vector DB needed |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | Runs locally, free, 384-dim vectors, no API cost per chunk |
| LLM | Groq API (`openai/gpt-oss-20b`) | Free tier, fast inference, swappable via one config variable |
| Testing | pytest | 16 unit + integration tests, real Postgres service container in CI |
| CI/CD | GitHub Actions | Lint → test (against real pgvector) → build, on every push |
| Deployment | Railway | Postgres + pgvector and the app both containerized and live |
| Frontend | Plain HTML/CSS/JS | No build step — served directly by FastAPI as a static file |

---

## How it works

1. **Upload** — a PDF is uploaded, text is extracted page-by-page (PyMuPDF), split into overlapping word-based chunks, embedded locally, and stored in Postgres alongside their vectors.
2. **Query** — your question is embedded the same way, and pgvector finds the most semantically similar chunks *within that specific document* using cosine distance, computed directly in SQL.
3. **Generate** — the retrieved chunks are inserted into a prompt that explicitly instructs the model not to use outside knowledge, then sent to Groq at low temperature for a grounded, low-hallucination answer.
4. **Cite** — every answer returns the source chunks and their page numbers, so you can verify the answer against the original document.

---

## Design decisions worth knowing about

- **Chunking uses overlapping windows, not hard cuts.** If a sentence carrying key information gets split exactly at a chunk boundary, its embedding can lose meaning. Overlap lets context bleed across the boundary.
- **Documents and chunks are separate tables (one-to-many)**, not one denormalized blob — this keeps page-level citation accurate and lets each chunk carry its own embedding independently.
- **Queries are scoped to a single `document_id`.** Without this, a question about Document A could retrieve and answer using chunks from Document B — technically grounded, but grounded in the wrong document.
- **If retrieval finds nothing relevant, the LLM is never called.** This is both a cost optimization and a hallucination guard — an honest "I don't have enough information" beats a confident, made-up answer.
- **The embedding model is cached in memory (`lru_cache`)**, loaded once per process rather than per request — loading from disk takes real time and shouldn't happen on every query.
- **The LLM provider/model name lives in one config variable.** This paid off directly: midway through building, Groq deprecated the original model (`llama3-8b-8192`) entirely. Swapping to the new recommended model (`openai/gpt-oss-20b`) took one line, not a refactor.
- **CI runs tests against a real Postgres + pgvector service container**, not a mock — catching real SQL/vector issues, not just Python logic errors.

---

## Known simplifications (and what I'd change for "real" production)

- Uploaded PDFs are stored on local/ephemeral disk, not object storage (S3, etc.) — fine for a demo, not durable for production.
- No authentication — anyone with the URL can upload and query. Would add auth before any real multi-user use.
- Token counts are approximated by word count, not a real tokenizer — good enough for a portfolio project, not for cost-accurate production billing.
- CORS is wide open (`allow_origins=["*"]`) to let the static frontend call the API from any origin — would scope this to a specific domain in production.

---

## Running it locally

```bash
git clone <https://github.com/Ajha2005/DocuQuery>
cd docuquery

cp .env.example .env
# then fill in your own GROQ_API_KEY in .env

docker compose up -d        # starts Postgres + pgvector on port 5433
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Then open `http://localhost:8000` in your browser.

## Running the tests

```bash
python -m pytest -v
```

---
