from app.llm import chat
from app.retrieval import search
from app.config import TOP_K


SYSTEM_PROMPT = """
You are the Cyberify assistant.

Rules you must follow:

1. Answer ONLY from the CONTEXT below.
2. Never use outside knowledge.
3. If the context does not contain the answer, reply exactly:
   "I could not find this in the documents."
4. Cite the source number in square brackets after every fact,
   like [1].
5. Never invent information that is not present in the context.
6. Be brief and clear.
"""


def build_context(
    hits: list[dict],
) -> str:
    """
    Number every retrieved chunk so the model
    can cite the source.
    """

    blocks = []

    for i, hit in enumerate(
        hits,
        start=1,
    ):
        blocks.append(
            f"[{i}] "
            f"({hit['source']}, "
            f"chunk {hit['chunk_index']})\n"
            f"{hit['content']}"
        )

    return "\n\n".join(
        blocks
    )


def answer_question(
    question: str,
    top_k: int = TOP_K,
    source: str | None = None,
) -> dict:
    """
    Answer a question using RAG.

    source=None:
        Search all documents.

    source="resume.docx":
        Search only that document.
    """

    hits = search(
        question,
        top_k=top_k,
        source=source,
    )

    if not hits:
        return {
            "answer":
                "I could not find this in the documents.",
            "sources": [],
            "used_context": False,
            "source_filter": source,
        }

    context = build_context(
        hits
    )

    user_prompt = (
        f"CONTEXT:\n"
        f"{context}\n\n"
        f"QUESTION:\n"
        f"{question}"
    )

    answer = chat(
        SYSTEM_PROMPT,
        user_prompt,
    )

    return {
        "answer": answer,

        "sources": [
            {
                "n": i,
                "title": hit["title"],
                "source": hit["source"],
                "chunk_index":
                    hit["chunk_index"],
                "score": round(
                    float(hit["score"]),
                    4,
                ),
            }
            for i, hit in enumerate(
                hits,
                start=1,
            )
        ],

        "used_context": True,

        "source_filter": source,
    }