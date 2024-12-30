from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline
import os
from pathlib import Path
import json

# Flask-app configuratie
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/kba": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

# FAISS opslaglocatie
FAISS_DIR = Path("/persistent/faiss_store")

# FAISS initialisatie
vectorstore = None  # Globale variabele om de vectorstore op te slaan

class SentenceTransformerWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/paraphrase-MiniLM-L3-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        return self.model.encode([query], show_progress_bar=False)[0]

embeddings_model = SentenceTransformerWrapper()
nlp_pipeline = pipeline("text-generation", model="distilgpt2")

# Controleer of FAISS-bestand bestaat
if FAISS_DIR.exists():
    vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings_model)

@app.route("/upload", methods=["POST"])
def upload_documents():
    global vectorstore
    if 'files' not in request.files:
        return jsonify({"error": "Geen bestanden ontvangen"}), 400

    files = request.files.getlist("files")
    documents = []

    for file in files:
        content = file.read().decode('utf-8')
        texts = content.split('\n')
        file_documents = [Document(page_content=text.strip(), metadata={"source": file.filename}) for text in texts if text.strip()]
        documents.extend(file_documents)

    document_texts = [doc.page_content for doc in documents]

    # Update of maak nieuwe FAISS vectorstore
    if vectorstore is None:
        vectorstore = FAISS.from_texts(document_texts, embeddings_model)
    else:
        vectorstore.add_texts(document_texts)

    # Sla FAISS op naar bestand
    vectorstore.save_local(str(FAISS_DIR))

    return jsonify({"message": f"{len(documents)} documenten succesvol geupload en verwerkt"})

@app.route("/kba", methods=["POST"])
def answer_question():
    global vectorstore

    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag = data.get("vraag", "")

    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    if vectorstore is None:
        return jsonify({"error": "Geen documenten beschikbaar. Upload eerst documenten."}), 400

    try:
        relevante_documenten = vectorstore.similarity_search(vraag, k=3)
        context = "\n".join([doc.page_content for doc in relevante_documenten])

        prompt = (
            f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
            f"{context}\n\n"
            f"Vraag: {vraag}\n"
            f"Antwoord (geef alleen het relevante deel van de context):"
        )

        result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
        antwoord = result[0]['generated_text']

        return jsonify({"vraag": vraag, "antwoord": antwoord})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Webservice draait correct!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000))