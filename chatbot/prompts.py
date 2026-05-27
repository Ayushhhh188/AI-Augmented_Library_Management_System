def build_prompt(context: str, question: str) -> str:
    return f"""You are a document assistant. Answer the question using ONLY the information provided.

Context:
{context}

Question: {question}

Write a clear answer in plain prose. Do not use bullet points, step labels, or numbered lists.
Do not quote the context. Do not show reasoning, drafts, or notes.
Only use facts from the context. If the answer is not in the context, say: "The information is not present in the provided documents."

Answer:"""