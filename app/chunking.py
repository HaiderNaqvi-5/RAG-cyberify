from app.config import CHUNK_CHARS, CHUNK_OVERLAP


def split_text(
    text: str,
    max_chars: int = CHUNK_CHARS,
    overlap: int = CHUNK_OVERLAP
) -> list[str]:

    # Split markdown into paragraphs
    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:

        # If adding the paragraph still fits,
        # keep it in the current chunk
        candidate = (
            f"{current}\n\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= max_chars:
            current = candidate
            continue

        # Current chunk is full
        if current:
            chunks.append(current.strip())

        # Start the next chunk with the WHOLE paragraph
        # instead of arbitrary characters from the previous chunk
        current = paragraph

    if current:
        chunks.append(current.strip())

    return chunks