from app.rag import answer_question


result = answer_question(
    "How long does the Cyberify internship last?"
)

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")
print(result["sources"])

print("\nUSED CONTEXT:")
print(result["used_context"])