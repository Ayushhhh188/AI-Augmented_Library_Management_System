def build_prompt(context: str, question: str, library_docs: list) -> str:
    catalog_lines = []
    for doc in library_docs or []:
        title = doc.get("title") or "Untitled"
        filename = doc.get("filename") or ""
        if filename and filename != title:
            catalog_lines.append(f"- {title} ({filename})")
        else:
            catalog_lines.append(f"- {title}")

    catalog = "\n".join(catalog_lines) if catalog_lines else "(no documents in the library)"
    context_block = context.strip() if context and context.strip() else "(no matching document excerpts)"

    return f"""You are a library document assistant. Answer using ONLY the library list and the retrieved excerpts.

Library documents currently in the database:
{catalog}

Retrieved excerpts:
{context_block}

Question: {question}

Rules:
- Use only facts from the library list and the retrieved excerpts.
- If the user asks whether a file or document is present, answer from the library list only. Say yes only if a listed title or filename matches. If it is present, name the exact title.
- If the user asks what a document says, use only the retrieved excerpts. If the excerpts do not contain the answer, say: "The information is not present in the provided documents."
- Do not invent policies, dates, organizations, or other facts that are not in the excerpts or library list.
- Write a clear answer in plain prose. Do not use bullet points, step labels, or numbered lists.
- Do not quote the excerpts. Do not show reasoning, drafts, or notes.

Answer:"""
