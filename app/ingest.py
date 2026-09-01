from app import db
from app.chunking import split_text
from app.embeddings import embed_texts, to_pgvector


def ingest_document(title: str, source: str, text: str) -> dict:

    chunks = split_text(text)

    if not chunks:
        raise ValueError("Document is empty.")

    doc = db.execute(
        """
        INSERT INTO documents (title, source)
        VALUES (%s, %s)
        RETURNING id, title, source
        """,
        (title, source),
    )

    vectors = embed_texts(chunks)

    for i, (content, vector) in enumerate(zip(chunks, vectors)):
        db.execute(
            """
            INSERT INTO chunks
            (
                document_id,
                chunk_index,
                content,
                n_chars,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s::vector)
            """,
            (
                doc["id"],
                i,
                content,
                len(content),
                to_pgvector(vector),
            ),
        )

    return {
        "document_id": doc["id"],
        "title": title,
        "source": source,
        "chunks": len(chunks),
    }


def list_documents() -> list[dict]:
    return db.query(
        """
        SELECT
            d.id,
            d.title,
            d.source,
            d.created_at,
            COUNT(c.id)::int AS chunk_count
        FROM documents d
        LEFT JOIN chunks c
            ON c.document_id = d.id
        GROUP BY d.id
        ORDER BY d.id
        """
    )
def delete_document(document_id: int) -> int:
    row = db.execute(
        "DELETE FROM documents WHERE id = %s RETURNING id",
        (document_id,),
    )

    return 1 if row else 0


def replace_document(
    document_id: int,
    title: str,
    source: str,
    text: str,
) -> dict:

    chunks = split_text(text)

    if not chunks:
        raise ValueError("Document is empty.")

    existing = db.query(
        "SELECT id FROM documents WHERE id = %s",
        (document_id,)
    )

    if not existing:
        raise ValueError("Document not found.")

    db.execute(
        """
        UPDATE documents
        SET title = %s,
            source = %s
        WHERE id = %s
        """,
        (title, source, document_id)
    )

    db.execute(
        """
        DELETE FROM chunks
        WHERE document_id = %s
        """,
        (document_id,)
    )

    vectors = embed_texts(chunks)

    for i, (content, vector) in enumerate(zip(chunks, vectors)):
        db.execute(
            """
            INSERT INTO chunks
            (
                document_id,
                chunk_index,
                content,
                n_chars,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s::vector)
            """,
            (
                document_id,
                i,
                content,
                len(content),
                to_pgvector(vector)
            )
        )

    return {
        "document_id": document_id,
        "title": title,
        "source": source,
        "chunks": len(chunks),
    }