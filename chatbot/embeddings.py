from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)


def create_embedding(text):

    return embedding_model.encode(
        text,
        normalize_embeddings=True
    ).tolist()