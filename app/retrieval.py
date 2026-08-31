from app import db
from app.config import TOP_K, MIN_SCORE
from app.embeddings import embed_one, to_pgvector


SEARCH_SQL = """
SELECT
    c.id,
    c.content,
    c.chunk_index,
    d.title,
    d.source,
    1 - (c.embedding <=> %s::vector) AS score
FROM chunks c
JOIN documents d
    ON d.id = c.document_id
ORDER BY c.embedding <=> %s::vector
LIMIT %s
"""


def search(
    question: str,
    top_k: int = TOP_K,
    min_score: float = MIN_SCORE
) -> list[dict]:

    vector = to_pgvector(embed_one(question))

    rows = db.query(
        SEARCH_SQL,
        (vector, vector, top_k)
    )

    return [
        row for row in rows
        if row["score"] >= min_score
    ]