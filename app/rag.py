from app.llm import chat
from app.retrieval import search
from app.config import TOP_K



SYSTEM_PROMPT = """
You are the Cyberify assistant.

Rules:
1. Answer ONLY from the provided CONTEXT.
2. Never use outside knowledge.
3. Read ALL retrieved context blocks before answering.
4. Prefer the context that most directly answers the question,
   even if it is not source [1].
5. If multiple sources are relevant, compare them before answering.
6. If the context does not contain the answer, reply exactly:
   "I could not find this in the documents."
7. Cite supporting source numbers in square brackets, like [1].
8. Keep answers brief and factual.
"""


def build_context(hits: list[dict]) -> str:

    blocks = []

    for i, hit in enumerate(hits, start=1):

        blocks.append(
            f"[{i}] "
            f"({hit['source']}, chunk {hit['chunk_index']})\n"
            f"{hit['content']}"
        )

    return "\n\n".join(blocks)


def answer_question(
    question: str,
    top_k: int = TOP_K
) -> dict:

    hits = search(
        question,
        top_k=top_k
    )

    if not hits:
        return {
            "answer": "I could not find this in the documents.",
            "sources": [],
            "used_context": False
        }

    context = build_context(hits)

    user_prompt = f"""
CONTEXT:
{context}

QUESTION:
{question}
"""

    answer = chat(
        SYSTEM_PROMPT,
        user_prompt
    )

    sources = []

    for i, hit in enumerate(hits, start=1):
        sources.append({
            "n": i,
            "title": hit["title"],
            "source": hit["source"],
            "chunk_index": hit["chunk_index"],
            "score": round(float(hit["score"]), 4)
        })

    return {
        "answer": answer,
        "sources": sources,
        "used_context": True
    }