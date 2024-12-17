from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline

# Flask-app configuratie
app = Flask(__name__)
CORS(app)

# Dummy variabelen voor FAISS-vectorstore en NLP-pipeline
vectorstore = None
nlp_pipeline = None

# Functie om services te initialiseren
def initialize_services():
    global vectorstore, nlp_pipeline

    # Wrapper voor SentenceTransformer
    class SentenceTransformerWrapper(Embeddings):
        def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
            self.model = SentenceTransformer(model_name)

        def embed_documents(self, texts):
            """Genereer embeddings voor documenten."""
            return self.model.encode(texts, show_progress_bar=True)

        def embed_query(self, query):
            """Genereer embedding voor een enkele vraag."""
            return self.model.encode([query], show_progress_bar=False)[0]

    # Initialiseer embeddings-model
    embeddings_model = SentenceTransformerWrapper()

    # Simuleer enkele documenten
    documents = [
        Document(page_content="Het lunchuur begint om 12:00 en duurt tot 13:00."),
        Document(page_content="De vergadering begint om 10:00."),
        Document(page_content="Het kantoor sluit om 17:00.")
    ]
    document_texts = [doc.page_content for doc in documents]

    # Maak de FAISS-vectorstore aan
    vectorstore = FAISS.from_texts(document_texts, embeddings_model)

    # Initialiseer NLP-pipeline (BLOOMZ)
    nlp_pipeline = pipeline("text-generation", model="bigscience/bloomz-1b7")

    print("Services succesvol geïnitialiseerd!")

# Functie voor ophalen van relevante documenten
def retrieve_documents(vraag, k=3):
    """Haal relevante documenten op uit de vectorstore."""
    if vectorstore is None:
        raise ValueError("Vectorstore is niet geïnitialiseerd.")
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]

# Functie voor antwoordgeneratie met BLOOMZ
def generate_answer(vraag, context):
    """Genereer een antwoord op basis van vraag en context."""
    prompt = (
        f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
        f"{context}\n\n"
        f"Vraag: {vraag}\n"
        f"Antwoord (geef alleen het relevante deel van de context):"
    )
    result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
    return result[0]['generated_text']

# Hoofdfunctie voor KBA
def kba_antwoord(vraag):
    """Verwerk de vraag en genereer het antwoord."""
    relevante_documenten = retrieve_documents(vraag)
    context = "\n".join(relevante_documenten)
    antwoord = generate_answer(vraag, context)
    return antwoord

# Root-endpoint voor controle
@app.route('/', methods=['GET'])
def home():
    """Controleer of de service actief is."""
    return jsonify({"message": "Webservice is actief!"})

# KBA-endpoint voor vragen en antwoorden
@app.route('/kba', methods=['POST'])
def kba_route():
    """API-endpoint voor KBA-functionaliteit."""
    try:
        data = request.json
        vraag = data.get("vraag", "Geen vraag ontvangen")
        antwoord = kba_antwoord(vraag)

        return jsonify({
            "vraag": vraag,
            "antwoord": antwoord
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main: Initialiseer services en start de Flask-app
if __name__ == '__main__':
    initialize_services()
    app.run(debug=True, host='0.0.0.0', port=5000)