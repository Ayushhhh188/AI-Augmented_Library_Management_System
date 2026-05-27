import os
import time
from google import genai

client = None

def _get_client():
    global client
    if client is None:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return client

def get_embedding(text: str) -> list:
    while True:
        try:
            result = _get_client().models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
            )
            time.sleep(0.5)  # 0.5s delay = max ~120 requests/min, under free tier limit
            return result.embeddings[0].values
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("Rate limited, waiting 60 seconds...")
                time.sleep(60)  # wait and retry automatically
            else:
                raise