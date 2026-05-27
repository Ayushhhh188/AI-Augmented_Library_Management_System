from chatbot.document_loader import load_documents
from chatbot.chunking import chunk_text
from chatbot.vector import add_chunks_to_vector_db


documents = load_documents()

for doc in documents:

    chunks = chunk_text(doc["content"])

    add_chunks_to_vector_db(
        chunks,
        metadata={
            "title": doc["title"]
        }
    )

    print(f"Ingested: {doc['title']}")

print("Vector DB build complete.")