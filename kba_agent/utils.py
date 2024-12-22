from langchain.docstore.document import Document

def load_documents(uploaded_files):
    documents = []
    for file_name, file_content in uploaded_files.items():
        content = file_content.decode('windows-1252')
        texts = content.split('\n')
        file_documents = [
            Document(page_content=text.strip(), metadata={"source": file_name})
            for text in texts if text.strip()
        ]
        documents.extend(file_documents)
    return documents