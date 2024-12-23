from flask import Flask, request, jsonify
from flask_cors import CORS
from kba_agent import RetrievalEngine, NLPEngine, load_documents
from config import Config
from langchain.docstore.document import Document
import os

# Flask-app configuratie
app = Flask(__name__)

# Laad configuratie vanuit config.py
app.config.from_object(Config)

# CORS-configuratie
CORS(app, resources={r"/kba": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

# Initialiseer de KBA-agent
retrieval_engine = RetrievalEngine()
nlp_engine = NLPEngine()

# Controleer of de vectorstore leeg is en voeg initiële documenten toe indien nodig
if not os.path.exists(os.path.join(retrieval_engine.vectorstore_path, "index.faiss")):
    print("Vectorstore is leeg. Voeg initiele documenten toe...")
    test_documents = [
        Document(page_content="Wat is AI?", metadata={"bron": "test.txt"}),
        Document(page_content="Machine learning is een subset van AI.", metadata={"bron": "test.txt"})
    ]
    retrieval_engine.add_documents(test_documents)
else:
    print("Vectorstore bestaat al.")

# Endpoint om vragen te beantwoorden
@app.route("/kba", methods=["POST"])
def kba_agent():
    data = request.get_json()
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    # Retrieve relevante documenten
    retrieved_docs = retrieval_engine.retrieve_documents(vraag)
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    # Genereer antwoord
    antwoord = nlp_engine.generate_answer(vraag, context)

    return jsonify({"vraag": vraag, "antwoord": antwoord, "context": context})

@app.route("/upload", methods=["POST"])
def upload_documents():
    uploaded_files = request.files.to_dict()
    documents = load_documents(uploaded_files)
    retrieval_engine.add_documents(documents)
    return jsonify({"message": "Documenten succesvol toegevoegd!"})

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))  # Gebruik de poort uit de omgeving
    print(f"Server draait op poort {port}")
    serve(app, host="0.0.0.0", port=port)