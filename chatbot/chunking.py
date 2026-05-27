from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,        # Increased from 700
        chunk_overlap=200,      # Increased from 120
        separators=["\n\n", "\n", ". ", " ", ""]  # Better boundary detection
    )
    chunks = splitter.split_text(text)
    return chunks