from chatbot.vector import search_vector_db
from chatbot.prompts import build_prompt
from chatbot.llm import generate_response


def run_rag_pipeline(question: str) -> str:
    results = search_vector_db(question, top_k=8)  # Fetch more chunks

    docs = results.get("documents", [[]])[0]

    if not docs:
        return "The information is not present in the provided documents."

    # Deduplicate and use top 5 chunks (up from 3)
    context_parts = []
    seen_chunks = set()

    for doc in docs[:5]:
        cleaned = " ".join(doc.split())
        if not _is_near_duplicate(cleaned, seen_chunks):
            seen_chunks.add(cleaned)
            context_parts.append(cleaned)

    if not context_parts:
        return "The information is not present in the provided documents."

    context = "\n\n".join(context_parts)

    prompt = build_prompt(context=context, question=question)
    return generate_response(prompt)


def _is_near_duplicate(text: str, existing: set, threshold: float = 0.8) -> bool:
    words = set(text.lower().split())
    if not words:
        return False
    for other in existing:
        other_words = set(other.lower().split())
        if not other_words:
            continue
        overlap = len(words & other_words) / min(len(words), len(other_words))
        if overlap >= threshold:
            return True
    return False