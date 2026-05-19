from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120
)

def chunk_text(text):

    if len(text) < 2000:
        return [text]

    return splitter.split_text(text)