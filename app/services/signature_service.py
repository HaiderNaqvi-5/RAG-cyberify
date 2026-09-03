from app import db


def get_document_id(
    filename: str,
) -> int | None:
    rows = db.query(
        """
        SELECT id
        FROM documents
        WHERE source = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (filename,),
    )

    if not rows:
        return None

    return rows[0]["id"]


def save_signature(
    document_id: int | None,
    filename: str,
    signature_bytes: bytes,
) -> int:
    # First try to find an existing signature
    # using the generated resume filename.
    existing = db.query(
        """
        SELECT id
        FROM signatures
        WHERE filename = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (filename,),
    )

    if existing:
        signature_id = existing[0]["id"]

        db.query(
            """
            UPDATE signatures
            SET
                document_id = %s,
                signature_png = %s,
                filename = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id
            """,
            (
                document_id,
                signature_bytes,
                filename,
                signature_id,
            ),
        )

        return signature_id

    rows = db.query(
        """
        INSERT INTO signatures (
            document_id,
            filename,
            signature_png
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (
            document_id,
            filename,
            signature_bytes,
        ),
    )

    return rows[0]["id"]