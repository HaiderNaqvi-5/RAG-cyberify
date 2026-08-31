from pathlib import Path

from app.ingest import ingest_document, list_documents


text = Path("seed/internship-faq.md").read_text(encoding="utf-8")
text = Path("seed/My_Resume.md").read_text(encoding="utf-8")

result = ingest_document(
    title="Cyberify Internship FAQ",
    source="internship-faq.md",
    text=text,
)

print("INGEST RESULT:")
print(result)

print("\nDOCUMENTS:")
print(list_documents())