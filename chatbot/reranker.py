from sentence_transformers import CrossEncoder


# ---------------------------------
# Cross Encoder Reranker
# ---------------------------------
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank(query, documents):

    if not documents:
        return []

    # ---------------------------------
    # Query-document pairs
    # ---------------------------------
    pairs = [
        [query, doc["text"]]
        for doc in documents
    ]

    # ---------------------------------
    # Predict relevance scores
    # ---------------------------------
    scores = reranker.predict(pairs)

    # ---------------------------------
    # Attach scores
    # ---------------------------------
    for doc, score in zip(documents, scores):

        doc["rerank_score"] = float(score)

    # ---------------------------------
    # Sort by relevance
    # ---------------------------------
    documents.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    # ---------------------------------
    # Return top reranked docs
    # ---------------------------------
    return documents[:4]