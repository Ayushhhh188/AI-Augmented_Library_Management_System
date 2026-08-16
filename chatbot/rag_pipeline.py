from chatbot.vector import search_vector_db
from chatbot.prompts import build_prompt
from chatbot.llm import generate_response


def run_rag_pipeline(question: str, library_docs: list) -> dict:
    results = search_vector_db(question, top_k=8)

    docs = results.get("documents", [[]])[0] or []
    metas = results.get("metadatas", [[]])[0] or []

    context_parts = []
    seen_chunks = set()
    kept_metas = []

    for i, doc in enumerate(docs[:5]):
        cleaned = " ".join(doc.split())
        if not _is_near_duplicate(cleaned, seen_chunks):
            seen_chunks.add(cleaned)
            context_parts.append(cleaned)
            kept_metas.append(metas[i] if i < len(metas) else {})

    if not library_docs and not context_parts:
        return {
            "answer": "The information is not present in the provided documents.",
            "sources": [],
        }

    context = "\n\n".join(context_parts)
    prompt = build_prompt(context=context, question=question, library_docs=library_docs)
    answer = generate_response(prompt)
    sources = _match_sources(question, kept_metas, library_docs)

    return {"answer": answer, "sources": sources}


def _normalize(text: str) -> str:
    return "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in (text or ""))


def _stem_name(text: str) -> str:
    name = _normalize(text).strip()
    for ext in (" pdf", " docx", " doc", " txt"):
        if name.endswith(ext):
            name = name[: -len(ext)].strip()
    return " ".join(name.split())


def _titles_match(left: str, right: str) -> bool:
    a = _stem_name(left)
    b = _stem_name(right)
    return bool(a and b and (a == b or a in b or b in a))


def _match_sources(question: str, retrieved_metadatas: list, library_docs: list) -> list:
    sources = []
    seen = set()

    def add(doc):
        doc_id = doc.get("id")
        if not doc_id or doc_id in seen:
            return
        seen.add(doc_id)
        sources.append({"id": doc_id, "title": doc.get("title") or "Untitled"})

    for meta in retrieved_metadatas or []:
        retrieved_title = (meta or {}).get("title") or ""
        for doc in library_docs or []:
            if _titles_match(retrieved_title, doc.get("title") or "") or _titles_match(
                retrieved_title, doc.get("filename") or ""
            ):
                add(doc)

    question_norm = _stem_name(question)
    for doc in library_docs or []:
        title = _stem_name(doc.get("title") or "")
        filename = _stem_name(doc.get("filename") or "")
        if title and title in question_norm:
            add(doc)
        elif filename and filename in question_norm:
            add(doc)

    return sources


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
