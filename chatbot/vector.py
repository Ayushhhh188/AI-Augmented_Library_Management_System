import chromadb

from chatbot.embeddings import create_embedding


client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


# ---------------------------------
# ADD DOCUMENTS
# ---------------------------------
def add_to_vector_db(chunked_documents):

    for doc in chunked_documents:

        text = doc["text"]

        page = doc["page"]

        metadata = doc["metadata"]

        chunk_id = doc["chunk_id"]

        embedding = create_embedding(text)

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[f"{metadata['filename']}_{chunk_id}"],
            metadatas=[{
                "source": metadata.get("filename"),
                "document_type": metadata.get("document_type"),
                "department": metadata.get("department"),
                "tags": ", ".join(metadata.get("tags", [])),
                "page": page,
                "access_level": metadata.get("access_level")
            }]
        )


# ---------------------------------
# SEARCH
# ---------------------------------
def search_documents(query, top_k=15):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    final_results = []

    for doc, meta, score in zip(
        documents,
        metadatas,
        distances
    ):

        similarity = 1 - score

        # -----------------------------
        # HALLUCINATION FILTER
        # -----------------------------
        if similarity < 0.15:
            continue

        final_results.append({
            "text": doc,
            "metadata": meta,
            "similarity": round(similarity, 3)
        })

    return final_results