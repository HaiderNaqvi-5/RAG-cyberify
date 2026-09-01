"""Text in, a list of 1536 numbers out. This is the only place we embed."""

from openai import OpenAI

from app.config import OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIM

client = OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many strings in ONE API call."""
    if not texts:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    ordered = sorted(response.data, key=lambda d: d.index)

    return [d.embedding for d in ordered]


def embed_one(text: str) -> list[float]:
    return embed_texts([text])[0]


def to_pgvector(vector: list[float]) -> str:
    """Convert Python list to PostgreSQL vector literal."""

    if len(vector) != EMBEDDING_DIM:
        raise ValueError(
            f"Expected {EMBEDDING_DIM} numbers, got {len(vector)}"
        )

    return "[" + ",".join(f"{x:.7f}" for x in vector) + "]"