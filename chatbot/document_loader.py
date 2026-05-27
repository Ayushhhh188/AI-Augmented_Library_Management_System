import os
import PyPDF2
from docx import Document


UPLOAD_FOLDER = "static/uploads"


def load_documents():

    documents = []

    for filename in os.listdir(UPLOAD_FOLDER):

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        text = ""

        try:

            # TXT
            if filename.lower().endswith(".txt"):

                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

            # PDF
            elif filename.lower().endswith(".pdf"):

                with open(filepath, "rb") as f:

                    reader = PyPDF2.PdfReader(f)

                    text = "\n".join(
                        [page.extract_text() or "" for page in reader.pages]
                    )

            # DOCX
            elif filename.lower().endswith((".docx", ".doc")):

                doc = Document(filepath)

                text = "\n".join(
                    [para.text for para in doc.paragraphs]
                )

            if text.strip():

                documents.append({
                    "title": filename,
                    "content": text
                })

        except Exception as e:

            print(f"Error loading {filename}: {e}")

    return documents