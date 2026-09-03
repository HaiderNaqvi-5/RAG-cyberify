import base64
from pathlib import Path

from fastapi import HTTPException


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

MAX_SIGNATURE_SIZE = (
    2 * 1024 * 1024
)


def validate_filename(
    filename: str,
) -> str:
    safe_filename = Path(
        filename
    ).name

    if not safe_filename.lower().endswith(
        ".docx"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid resume filename."
            ),
        )

    return safe_filename


def decode_signature_png(
    signature_data: str,
) -> bytes:
    if not signature_data.startswith(
        "data:image/png;base64,"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Signature must be a PNG image."
            ),
        )

    try:
        encoded_data = (
            signature_data.split(
                ",",
                1,
            )[1]
        )

        signature_bytes = (
            base64.b64decode(
                encoded_data,
                validate=True,
            )
        )

    except (
        ValueError,
        base64.binascii.Error,
        IndexError,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid signature image data."
            ),
        )

    if not signature_bytes.startswith(
        PNG_SIGNATURE
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid PNG signature."
            ),
        )

    if (
        len(signature_bytes)
        > MAX_SIGNATURE_SIZE
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Signature image is too large."
            ),
        )

    return signature_bytes