import os

from chatbot.document_loader import extract_text

from chatbot.chunking import chunk_documents

from chatbot.vector import add_to_vector_db


UPLOAD_FOLDER = "static/uploads"


def ingest_documents():

    for filename in os.listdir(UPLOAD_FOLDER):

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        print(f"\nIngesting: {filename}")

        # -----------------------------
        # Extract pages + metadata
        # -----------------------------
        pages = extract_text(file_path)

        print(f"Pages extracted: {len(pages)}")

        # -----------------------------
        # Chunk
        # -----------------------------
        chunked_documents = chunk_documents(
            pages
        )

        print(
            f"Chunks created: "
            f"{len(chunked_documents)}"
        )

        # -----------------------------
        # Store
        # -----------------------------
        add_to_vector_db(
            chunked_documents
        )

        print("Stored in vector DB")


if __name__ == "__main__":

    ingest_documents()