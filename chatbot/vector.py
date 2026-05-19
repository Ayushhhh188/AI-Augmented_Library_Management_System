import chromadb

from chatbot.embeddings import create_embedding

# -------------------------------
# ChromaDB
# -------------------------------
client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_or_create_collection(
    name="documents"
)

# -------------------------------
# Add Chunks
# -------------------------------
def add_to_vector_db(chunks, title, file_path):

    for i, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{title}_{i}"],
            metadatas=[{
                "title": title,
                "source": file_path
            }]
        )

# -------------------------------
# Search
# -------------------------------
def search_documents(query):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    return results["documents"][0]