import chromadb
from chatbot.embeddings import get_embedding


client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_or_create_collection(
    name="library_documents"
)


def add_chunks_to_vector_db(chunks, metadata):

    for i, chunk in enumerate(chunks):

        embedding = get_embedding(chunk)

        collection.add(
            ids=[f"{metadata['title']}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[metadata]
        )


def search_vector_db(query, top_k=4):

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results