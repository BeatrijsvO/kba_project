from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline
import os

# Flask-app configuratie
app = Flask(__name__)
CORS(app)

# 1. Wrapper voor SentenceTransformer
class SentenceTransformerWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=False)

    def embed_query(self, query):
        return self.model.encode([query], show_progress_bar=False)[0]

embeddings_model = SentenceTransformerWrapper()

# 2. Initialiseer BLOOMZ pipeline
nlp_pipeline = pipeline("text-generation", model="google/flan-t5-small")

# 3. Vooraf ingestelde documenten
documents = [
    Document(page_content="Er wordt een lunchpauze van 30 minuten opgenomen tussen 12:00 en 13:30 uur."),
    Document(page_content="Overuren worden geregistreerd in het HR-portaal."),
    Document(page_content="Overuren worden gecompenseerd met 1,5 keer het normale uurtarief."),
]

# 4. Maak FAISS vectorstore
document_texts = [doc.page_content for doc in documents]
vectorstore = FAISS.from_texts(document_texts, embeddings_model)

def retrieve_documents(vraag, k=3):
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]

def generate_answer(vraag, context):
    prompt = f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n{context}\n\nVraag: {vraag}\nAntwoord:"
    result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
    return result[0]['generated_text']

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

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Running production server on port {port}...")
    serve(app, host="0.0.0.0", port=port)