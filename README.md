# RAG-cyberify

RAG-cyberify is a lightweight Retrieval-Augmented Generation application for grounding answers in local documents. It ingests source content into a PostgreSQL + pgvector database, chunks and embeds the text, retrieves relevant passages, and uses an LLM to answer questions based only on that retrieved context.

## Why this project exists

This project is useful for:

- Q&A over internal docs, resumes, policies, or FAQ content
- Building a local or self-hosted knowledge assistant
- Keeping answers grounded in retrieved documents instead of free-form hallucination
- Serving a simple browser UI and a REST API from the same codebase

## Features

- Document ingestion from raw text or file content
- Chunking and embeddings for semantic retrieval
- PostgreSQL + pgvector vector search
- Context-aware answer generation with OpenAI models
- FastAPI endpoints for document management and Q&A
- Simple frontend served from the `static/` folder
- Tests for ingestion, retrieval, and DB behavior

## Tech stack

- Python 3.11+
- FastAPI
- PostgreSQL with pgvector
- OpenAI embeddings and chat APIs
- HTML/CSS/JS frontend
- pytest for automated tests

## Repository structure

```text
RAG-cyberify/
├── app/                 # application logic (config, ingestion, retrieval, LLM, API)
├── db/                  # SQL schema and DB-related assets
├── seed/                # sample source documents
├── static/              # frontend HTML/CSS/JS assets
├── tests/               # automated tests
├── .env                 # local environment variables (not committed)
├── .env.example         # example environment configuration
├── .gitignore           # ignored local files
├── README.md            # project overview and setup instructions
├── requirements.txt     # Python dependencies
└── storage/             # local document storage
```

## Prerequisites

Before starting, make sure you have:

- Python 3.11 or newer
- PostgreSQL installed and running
- The pgvector extension enabled in your PostgreSQL instance
- An OpenAI API key

## Setup

1. Clone the repository and enter it:

```bash
cd /path/to/RAG-cyberify-master
```

2. Create and activate a virtual environment:

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your environment file:

```bash
cp .env.example .env
```

Then update `.env` with your values:

```env
OPENAI_API_KEY=your_openai_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cyberify_rag
DB_USER=cyberify
DB_PASSWORD=cyberify123
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
CHAT_MODEL=gpt-4o-mini
TOP_K=4
MIN_SCORE=0.20
CHUNK_CHARS=700
CHUNK_OVERLAP=120
```

5. Create your PostgreSQL database and ensure the `pgvector` extension is enabled.

## Running the app

Start the API server:

```bash
uvicorn app.main:api --reload
```

Then open the app in a browser:

- Frontend: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs

## API endpoints

```http
GET  /api/health
POST /api/ingest
POST /api/ingest/file
GET  /api/documents
DELETE /api/documents/{document_id}
POST /api/ask
```

### Example: ingest a document

```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Internship FAQ",
    "source": "seed/internship-faq.md",
    "text": "The internship is remote and open to students."
  }'
```

### Example: ask a question

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What types of internship roles are available?",
    "top_k": 4
  }'
```

## Testing

Run the automated test suite:

```bash
pytest -q
```

## Notes

- The application answers from retrieved context and does not rely on memorized knowledge alone.
- It is meant to be a grounded document Q&A system rather than a general-purpose chatbot.
- Frontend assets are served out of the `static/` directory.
- Local secrets should stay in `.env`, which is intentionally not committed.
