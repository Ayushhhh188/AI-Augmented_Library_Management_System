import PyPDF2

from docx import Document

def extract_text(file_path):

    content = ""

    try:

        if file_path.lower().endswith(".txt"):

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        elif file_path.lower().endswith(".pdf"):

            with open(file_path, "rb") as f:

                reader = PyPDF2.PdfReader(f)

                content = "\n".join([
                    page.extract_text() or ""
                    for page in reader.pages
                ])

        elif file_path.lower().endswith((".doc", ".docx")):

            docx_file = Document(file_path)

            content = "\n".join([
                p.text
                for p in docx_file.paragraphs
            ])

    except Exception as e:

        print("Extraction Error:", e)

    return content