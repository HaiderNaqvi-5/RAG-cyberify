from app.retrieval import search


question = "Which experience best demonstrates Haider's ability to handle millions of records?"

results = search(question)

print("\nQUESTION:")
print(question)

print("\nRESULTS:")

for result in results:
    print("-" * 50)
    print("Source:", result["source"])
    print("Chunk:", result["chunk_index"])
    print("Score:", result["score"])
    print("Content:")
    print(result["content"])