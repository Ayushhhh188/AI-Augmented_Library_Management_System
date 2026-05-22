from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=120,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def chunk_documents(pages):

    chunked_documents = []

    for page_data in pages:

        text = page_data["text"]
        page = page_data["page"]
        metadata = page_data["metadata"]

        chunks = splitter.split_text(text)

        for idx, chunk in enumerate(chunks):

            if len(chunk.strip()) < 80:
                continue

            chunked_documents.append({
                "text": chunk,
                "page": page,
                "chunk_id": f"{page}_{idx}",
                "metadata": metadata
            })

    return chunked_documents