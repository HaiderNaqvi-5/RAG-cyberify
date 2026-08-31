from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db, ingest, rag
from app.config import CHAT_MODEL, EMBEDDING_MODEL, TOP_K

api = FastAPI(title="Cyberify RAG", version="1.0")


class IngestBody(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    source: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)


class AskBody(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


@api.get("/api/health")
def health():
    rows = db.query("SELECT COUNT(*)::int AS chunks FROM chunks")
    return {
        "status": "ok",
        "chunks_indexed": rows[0]["chunks"],
        "embedding_model": EMBEDDING_MODEL,
        "chat_model": CHAT_MODEL,
    }


@api.post("/api/ingest", status_code=201)
def ingest_text(body: IngestBody):
    try:
        return ingest.ingest_document(
            body.title,
            body.source,
            body.text
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.post("/api/ingest/file", status_code=201)
async def ingest_file(file: UploadFile = File(...)):
    raw = await file.read()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Send a plain .txt or .md UTF-8 file."
        )

    return ingest.ingest_document(
        file.filename,
        file.filename,
        text
    )


@api.get("/api/documents")
def documents():
    return ingest.list_documents()


@api.delete("/api/documents/{document_id}")
def remove_document(document_id: int):
    if ingest.delete_document(document_id) == 0:
        raise HTTPException(
            status_code=404,
            detail="No document with that id"
        )

    return {"deleted": document_id}


@api.post("/api/ask")
def ask(body: AskBody):
    return rag.answer_question(
        body.question,
        top_k=body.top_k
    )


api.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@api.get("/")
def home():
    return FileResponse("static/index.html")