from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import os

# Flask-app configuratie
app = Flask(__name__)
CORS(app)

# Configuratie voor FAISS opslaglocatie
FAISS_DIR = Path("/persistent/faiss_store")

# Initialisatie van modellen
class SentenceTransformerWrapper:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        return self.model.encode([query], show_progress_bar=False)[0]

embeddings_model = SentenceTransformerWrapper()
nlp_pipeline = pipeline("text-generation", model="distilgpt2")  # Lichter model gekozen

# FAISS initialisatie
vectorstore = None
if FAISS_DIR.exists():
    vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings_model)

# Helperfunctie om FAISS te laden
def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        if FAISS_DIR.exists():
            vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings_model)
        else:
            raise ValueError("FAISS-bestand niet gevonden. Upload eerst documenten.")
    return vectorstore

# API-endpoints
@app.route("/upload", methods=["POST"])
def upload_documents():
    """Upload documenten en voeg toe aan de FAISS vectorstore."""
    if 'files' not in request.files:
        return jsonify({"error": "Geen bestanden ontvangen"}), 400

    files = request.files.getlist("files")
    documents = []

    for file in files:
        content = file.read().decode('utf-8')
        texts = content.split('\n')
        documents.extend(texts)

    document_texts = [text.strip() for text in documents if text.strip()]

    # Update of maak nieuwe FAISS vectorstore
    global vectorstore
    if vectorstore is None:
        vectorstore = FAISS.from_texts(document_texts, embeddings_model)
    else:
        vectorstore.add_texts(document_texts)

    # Sla FAISS op naar bestand
    vectorstore.save_local(str(FAISS_DIR))

    return jsonify({"message": f"{len(document_texts)} documenten succesvol geupload en verwerkt."})

@app.route("/kba", methods=["POST"])
def answer_question():
    """Beantwoord vragen met behulp van de FAISS vectorstore en een NLP-model."""
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag = data.get("vraag", "")

    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    try:
        vectorstore = get_vectorstore()
        relevante_documenten = vectorstore.similarity_search(vraag, k=3)
        context = "\n".join([doc.page_content for doc in relevante_documenten])

        prompt = (
            f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
            f"{context}\n\n"
            f"Vraag: {vraag}\n"
            f"Antwoord:"
        )

        result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
        antwoord = result[0]['generated_text']

        return jsonify({"vraag": vraag, "antwoord": antwoord})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Interne fout: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    """Controleer of de webservice draait."""
    return jsonify({"status": "Webservice draait correct!"})

# Start de applicatie
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))