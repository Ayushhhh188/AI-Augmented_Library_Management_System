import requests


OLLAMA_MODEL = "mistral"


def generate_answer(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {

              
                "temperature": 0,

                "top_p": 0.2,

                "num_predict": 400,

                "repeat_penalty": 1.2
            }
        }
    )

    return response.json()["response"]