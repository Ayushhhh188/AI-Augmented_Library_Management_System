def build_prompt(context, question):

    return f"""
You are an enterprise AI assistant.

Answer ONLY using the provided context.

If the answer is not found,
say:
"I could not find this information in the documents."

Context:
{context}

Question:
{question}
"""