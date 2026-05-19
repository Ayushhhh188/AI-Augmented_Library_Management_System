import requests

OLLAMA_MODEL = "phi3"

def generate_answer(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
    )

    return response.json()["response"]