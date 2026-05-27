import os
import re
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash"


def _clean_response(text: str) -> str:
    """
    Strip any chain-of-thought / reasoning that leaks into the output.
    """
    lines = text.splitlines()
    clean = []

    for line in lines:
        stripped = line.strip()

        if re.match(r'^\*\s*\*[^*]+\*\s*[:\*]', stripped):
            continue
        if re.match(r'^\*\s*["\u201c]', stripped):
            continue
        if re.match(r'^\*\s*(check|draft|note|wait|let me|self|word count|sentence|final polish|final draft|final version|final check|constraint)', stripped, re.IGNORECASE):
            continue

        clean.append(line)

    result = "\n".join(clean).strip()
    return result if result else text.strip()


def generate_response(prompt: str) -> str:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.9,
            max_output_tokens=1200,  # Raised — long procedural answers need room
        ),
    )
    return _clean_response(response.text)
