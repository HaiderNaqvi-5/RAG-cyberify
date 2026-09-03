from pathlib import Path

from fastapi import APIRouter, HTTPException

from app import db, ingest
from app.document_parser import extract_docx_text
from app.graph.resume_graph import resume_graph
from app.models.resume import (
    EditedResume,
    GeneratedResume,
    ResumeData,
)
from app.services.resume_generator import (
    update_resume_document,
)


router = APIRouter()


@router.post("/collect")
def collect_resume_data(data: ResumeData):
    return {
        "success": True,
        "message": "Resume information received successfully.",
        "data": data.model_dump(),
    }


@router.post("/generate-document")
def generate_document(data: ResumeData):
    try:
        result = resume_graph.invoke(
            {
                "resume_data": data,
            }
        )

        # Graph stopped because required information was missing
        missing_fields = result.get(
            "missing_fields",
            [],
        )

        if missing_fields:
            return {
                "success": False,
                "message": "Some resume information is missing.",
                "missing_fields": missing_fields,
            }

        # Graph encountered an error
        error = result.get("error")

        if error:
            violations = result.get(
                "guardrail_violations",
                [],
            )

            raise HTTPException(
                status_code=500,
                detail={
                    "message": error,
                    "guardrail_violations": violations,
                },
            )

        generated_resume = result.get(
            "generated_resume"
        )

        filename = result.get(
            "filename"
        )

        if not generated_resume or not filename:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Resume generation did not complete."
                ),
            )

        validated_resume = GeneratedResume(
            **generated_resume
        )

        return {
            "success": True,
            "filename": filename,
            "resume": validated_resume.model_dump(),
            "file_url": result.get(
                "file_url"
            ),

            # Keeping this temporarily for compatibility.
            # Nova frontend no longer needs to open it.
            "editor_url": result.get(
                "editor_url"
            ),

            "guardrail_passed": result.get(
                "guardrail_passed",
                False,
            ),
            "guardrail_violations": result.get(
                "guardrail_violations",
                [],
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "LangGraph resume generation failed:",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate resume document."
            ),
        )


@router.post("/update-document")
def update_document(data: EditedResume):
    """
    Save edits made inside the Nova Resume Editor.

    Workflow:
    1. Validate filename.
    2. Re-render the DOCX using the resume template.
    3. Overwrite the existing generated DOCX.
    4. Extract updated text.
    5. Replace or create the corresponding RAG document.
    """

    try:
        safe_filename = Path(
            data.filename
        ).name

        if not safe_filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename.",
            )

        if not safe_filename.lower().endswith(
            ".docx"
        ):
            raise HTTPException(
                status_code=400,
                detail="Only DOCX files can be updated.",
            )

        edited_data = data.model_dump()

        # Regenerate the existing DOCX using
        # the edited content from Nova.
        filename = update_resume_document(
            filename=safe_filename,
            edited_resume=edited_data,
        )

        file_path = (
            Path("storage/documents")
            / filename
        )

        if not file_path.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    "Updated resume file was not created."
                ),
            )

        # Extract the updated resume text.
        updated_text = extract_docx_text(
            str(file_path)
        )

        if not updated_text.strip():
            raise HTTPException(
                status_code=500,
                detail=(
                    "Updated resume contains no readable text."
                ),
            )

        # Search for an existing RAG document
        # associated with this generated resume.
        existing_docs = db.query(
            """
            SELECT id
            FROM documents
            WHERE source = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (filename,),
        )

        if existing_docs:
            document_id = (
                existing_docs[0]["id"]
            )

            rag_result = ingest.replace_document(
                document_id=document_id,
                title=filename,
                source=filename,
                text=updated_text,
            )

            rag_action = "reindexed"

        else:
            rag_result = ingest.ingest_document(
                title=filename,
                source=filename,
                text=updated_text,
            )

            rag_action = "indexed"

        return {
            "success": True,
            "message": (
                "Resume updated successfully."
            ),
            "filename": filename,
            "file_url": (
                f"/api/files/{filename}"
            ),
            "rag_action": rag_action,
            "rag_ingestion": rag_result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "Resume update failed:",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update resume document."
            ),
        )