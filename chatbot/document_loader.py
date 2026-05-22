import os
import json
import PyPDF2

from docx import Document


METADATA_FILE = "metadata/documents.json"


def load_metadata():

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            metadata_list = json.load(f)

        metadata_map = {
            item["filename"]: item
            for item in metadata_list
        }

        return metadata_map

    except Exception as e:
        print("Metadata Load Error:", e)
        return {}


DOCUMENT_METADATA = load_metadata()


def extract_text(file_path):

    pages = []

    filename = os.path.basename(file_path)

    metadata = DOCUMENT_METADATA.get(filename, {})

    try:

        # -----------------------------
        # TXT FILES
        # -----------------------------
        if file_path.lower().endswith(".txt"):

            with open(file_path, "r", encoding="utf-8") as f:

                text = f.read()

                pages.append({
                    "text": text,
                    "page": 1,
                    "metadata": metadata
                })

        # -----------------------------
        # PDF FILES
        # -----------------------------
        elif file_path.lower().endswith(".pdf"):

            with open(file_path, "rb") as f:

                reader = PyPDF2.PdfReader(f)

                for page_num, page in enumerate(reader.pages, start=1):

                    text = page.extract_text() or ""

                    if len(text.strip()) > 50:

                        pages.append({
                            "text": text,
                            "page": page_num,
                            "metadata": metadata
                        })

        # -----------------------------
        # DOCX FILES
        # -----------------------------
        elif file_path.lower().endswith((".doc", ".docx")):

            docx_file = Document(file_path)

            text = "\n".join([
                p.text
                for p in docx_file.paragraphs
            ])

            pages.append({
                "text": text,
                "page": 1,
                "metadata": metadata
            })

    except Exception as e:

        print("Extraction Error:", e)

    return pages