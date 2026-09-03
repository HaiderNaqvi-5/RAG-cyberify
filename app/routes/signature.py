from fastapi import APIRouter

from app.models.signature import (
    SignatureResponse,
    SignatureUpload,
)
from app.services.signature_service import (
    get_document_id,
    save_signature,
)
from app.validators.signature_validator import (
    decode_signature_png,
    validate_filename,
)


router = APIRouter()


@router.post(
    "/upload",
    response_model=SignatureResponse,
)
def upload_signature(
    body: SignatureUpload,
):
    safe_filename = validate_filename(
        body.filename
    )

    signature_bytes = (
        decode_signature_png(
            body.signature_data
        )
    )

    document_id = get_document_id(
        safe_filename
    )

    signature_id = save_signature(
        document_id=document_id,
        filename=safe_filename,
        signature_bytes=signature_bytes,
    )

    return {
        "success": True,
        "signature_id": signature_id,
        "filename": safe_filename,
        "size_bytes": len(
            signature_bytes
        ),
    }