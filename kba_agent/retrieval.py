import os
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer

class SentenceTransformerWrapper:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Genereer embeddings voor een lijst met teksten."""
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        """Genereer een embedding voor een enkele vraag."""
        return self.model.encode([query], show_progress_bar=False)[0]

class RetrievalEngine:
    def __init__(self, embeddings_model_name="sentence-transformers/all-MiniLM-L6-v2", vectorstore_path="vectorstore/"):
        self.embeddings_model = SentenceTransformerWrapper(embeddings_model_name)
        self.vectorstore_path = vectorstore_path
        self.vectorstore = self._load_vectorstore()

    def _load_vectorstore(self):
        """Laad of initialiseer de FAISS-vectorstore."""
        if os.path.exists(self.vectorstore_path):
            return FAISS.load_local(self.vectorstore_path, self.embeddings_model)
        return FAISS(self.embeddings_model)

    def add_documents(self, documents):
        """Voeg documenten toe aan de vectorstore."""
        document_texts = [doc.page_content for doc in documents]
        self.vectorstore.add_texts(document_texts)
        self.vectorstore.save_local(self.vectorstore_path)

    def retrieve_documents(self, vraag, k=3):
        """Haal de top k relevante documenten op uit de vectorstore."""
        return self.vectorstore.similarity_search(vraag, k=k)