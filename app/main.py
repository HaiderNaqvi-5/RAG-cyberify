from pathlib import Path

import httpx

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db, ingest, rag
from app.config import CHAT_MODEL, EMBEDDING_MODEL, TOP_K
from app.document_parser import extract_docx_text

from app.routes.resume import router as resume_router
from app.routes.signature import router as signature_router


api = FastAPI(
    title="Cyberify RAG",
    version="1.0",
)


api.include_router(
    resume_router,
    prefix="/api/resume",
    tags=["Resume"],
)

api.include_router(
    signature_router,
    prefix="/api/signature",
    tags=["Signature"],
)
DOCUMENT_DIR = Path("storage/documents")
DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)

class IngestBody(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    source: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)


class AskBody(BaseModel):
    question: str = Field(
        min_length=3
    )

    top_k: int = Field(
        default=TOP_K,
        ge=1,
        le=20,
    )

    source: str | None = None


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
        top_k=body.top_k,
        source=body.source,
    )


api.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)
@api.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = DOCUMENT_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    rag_result = None

    if file.filename.lower().endswith(".docx"):
        text = extract_docx_text(str(file_path))

        rag_result = ingest.ingest_document(
            title=file.filename,
            source=file.filename,
            text=text,
        )

    return {
        "filename": file.filename,
        "file_url": f"/api/files/{file.filename}",
        "rag_ingestion": rag_result,
    }
@api.get("/api/files/{filename}")
def get_file(filename: str):
    file_path = DOCUMENT_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename=filename,
    )
@api.post("/api/onlyoffice/callback/{filename}")
async def onlyoffice_callback(
    filename: str,
    payload: dict,
):
    safe_filename = Path(filename).name

    status = payload.get("status")

    print("ONLYOFFICE CALLBACK")
    print("File:", safe_filename)
    print("Status:", status)

    if status in [2, 6]:

        download_url = payload.get("url")

        if not download_url:
            print("No download URL received.")
            return {"error": 0}

        print("Downloading edited file from:")
        print(download_url)

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:

                response = await client.get(
                    download_url
                )

                response.raise_for_status()

        except httpx.HTTPError as e:
            print("Failed to download edited file:")
            print(e)

            return {
                "error": 1
            }

        file_path = DOCUMENT_DIR / safe_filename

        with open(file_path, "wb") as f:
            f.write(response.content)

        print("Edited file saved successfully:")
        print(file_path)

        # ---------------------------------------------
        # RE-INDEX UPDATED DOCX INTO RAG
        # ---------------------------------------------

        try:
            updated_text = extract_docx_text(
                str(file_path)
            )

            existing_docs = db.query(
                """
                SELECT id
                FROM documents
                WHERE source = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (safe_filename,)
            )

            if existing_docs:
                document_id = existing_docs[0]["id"]

                rag_result = ingest.replace_document(
                    document_id=document_id,
                    title=safe_filename,
                    source=safe_filename,
                    text=updated_text,
                )

                print("RAG re-index completed:")
                print(rag_result)

            else:
                print(
                    "No existing RAG document found."
                )

                rag_result = ingest.ingest_document(
                    title=safe_filename,
                    source=safe_filename,
                    text=updated_text,
                )

                print("RAG ingestion completed:")
                print(rag_result)

        except Exception as e:
            print("RAG re-index failed:")
            print(e)

    return {
        "error": 0
    }
@api.get("/")
def home():
    return FileResponse("static/index.html")