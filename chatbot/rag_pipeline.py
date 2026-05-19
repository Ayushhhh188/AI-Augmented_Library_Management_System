from chatbot.vector import search_documents

from chatbot.llm import generate_answer

from chatbot.prompts import build_prompt

def ask_rag(query):

    retrieved_chunks = search_documents(query)

    context = "\n\n".join(retrieved_chunks)

    prompt = build_prompt(
        context,
        query
    )

    answer = generate_answer(prompt)

    return answer