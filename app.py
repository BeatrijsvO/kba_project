# Productie omgeving
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline

# Flask-app configuratie
app = Flask(__name__)
CORS(app)  # Sta CORS toe voor API-aanroepen

# 1. Definieer een Wrapper voor SentenceTransformer
class SentenceTransformerWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Genereer embeddings voor een lijst met teksten."""
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        """Genereer een embedding voor een enkele vraag."""
        return self.model.encode([query], show_progress_bar=False)[0]

# Initialiseer het embeddingsmodel
embeddings_model = SentenceTransformerWrapper()

# 2. Initialiseer BLOOMZ pipeline
nlp_pipeline = pipeline("text-generation", model="bigscience/bloomz-1b7")

# 3. Statische documenten (voor testen zonder Colab upload)
documents = [
    Document(page_content="Er wordt een lunchpauze van 30 minuten opgenomen tussen 12:00 en 13:30 uur."),
    Document(page_content="Overuren worden geregistreerd in het HR-portaal."),
    Document(page_content="Overuren worden gecompenseerd met 1,5 keer het normale uurtarief."),
]

print(f"Aantal documenten: {len(documents)}")

# 4. Maak de FAISS-vectorstore
document_texts = [doc.page_content for doc in documents]
vectorstore = FAISS.from_texts(document_texts, embeddings_model)

# Functie om relevante documenten op te halen
def retrieve_documents(vraag, k=3):
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]

# Functie om een antwoord te genereren
def generate_answer(vraag, context):
    prompt = f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n{context}\n\nVraag: {vraag}\nAntwoord:"
    result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
    return result[0]['generated_text']

# Endpoint om vragen te beantwoorden
@app.route("/kba", methods=["POST"])
def answer_question():
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    relevante_documenten = retrieve_documents(vraag)
    context = "\n".join(relevante_documenten)
    antwoord = generate_answer(vraag, context)

    return jsonify({"vraag": vraag, "antwoord": antwoord})

# Start de server met Waitress
if __name__ == "__main__":
    from waitress import serve
    import os
    print("Running production server with Waitress...")
    port = int(os.environ.get("PORT", 5000))  
    serve(app, host="0.0.0.0", port=port)