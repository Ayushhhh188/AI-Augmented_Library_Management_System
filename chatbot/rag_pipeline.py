from chatbot.vector import search_documents

from chatbot.llm import generate_answer

from chatbot.prompts import build_prompt

from chatbot.reranker import rerank


def ask_rag(query):

    # ---------------------------------
    # INITIAL VECTOR RETRIEVAL
    # ---------------------------------
    retrieved_chunks = search_documents(
        query,
        top_k=12
    )

    # ---------------------------------
    # NO DOCUMENTS FOUND
    # ---------------------------------
    if not retrieved_chunks:

        return (
            "I could not find relevant information "
            "in the uploaded documents."
        )

    # ---------------------------------
    # RERANK DOCUMENTS
    # ---------------------------------
    retrieved_chunks = rerank(
        query,
        retrieved_chunks
    )

    # ---------------------------------
    # STILL NO DOCUMENTS AFTER RERANK
    # ---------------------------------
    if not retrieved_chunks:

        return (
            "I could not find relevant information "
            "in the uploaded documents."
        )

    contexts = []

    used_sources = set()

    # ---------------------------------
    # BUILD STRUCTURED CONTEXT
    # ---------------------------------
    for idx, item in enumerate(retrieved_chunks):

        text = item["text"]

        metadata = item["metadata"]

        similarity = item.get(
            "similarity",
            0
        )

        rerank_score = item.get(
            "rerank_score",
            0
        )

        source = metadata.get(
            "source",
            "Unknown"
        )

        page = metadata.get(
            "page",
            "N/A"
        )

        department = metadata.get(
            "department",
            "General"
        )

        doc_type = metadata.get(
            "document_type",
            "Document"
        )

        citation = (
            f"[SOURCE: {source} | PAGE: {page}]"
        )

        used_sources.add(citation)

        formatted_context = f"""
DOCUMENT #{idx + 1}

DOCUMENT TYPE: {doc_type}

DEPARTMENT: {department}

VECTOR SIMILARITY: {similarity}

RERANK SCORE: {rerank_score}

{citation}

CONTENT:
{text}
"""

        contexts.append(formatted_context)

    # ---------------------------------
    # FINAL CONTEXT
    # ---------------------------------
    final_context = "\n\n".join(contexts)

    # ---------------------------------
    # BUILD PROMPT
    # ---------------------------------
    prompt = build_prompt(
        final_context,
        query
    )

    # ---------------------------------
    # GENERATE ANSWER
    # ---------------------------------
    answer = generate_answer(prompt)

    return answer