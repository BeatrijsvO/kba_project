# ALLEEN IN productie omgeving
# uitvoeren in cmd: pip install -U langchain sentence-transformers faiss-cpu langchain-community flask flask-cors
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline
import os

@app.route("/kba", methods=["POST"])
app = Flask(__name__)
CORS(app)  # Sta verzoeken van andere domeinen toe

# 2. Definieer een Wrapper voor SentenceTransformer
class SentenceTransformerWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Genereer embeddings voor een lijst met teksten."""
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        """Genereer een embedding voor een enkele vraag."""
        return self.model.encode([query], show_progress_bar=False)[0]

# Initialiseer het embeddingsmodel via de wrapper
embeddings_model = SentenceTransformerWrapper()

# 3. Initialiseer BLOOMZ model pipeline
nlp_pipeline = pipeline("text-generation", model="bigscience/bloomz-1b7")

# 4. Upload documenten
uploaded = files.upload()
documents = []

for file_name, file_content in uploaded.items():
    content = file_content.decode('windows-1252')  # Decodeer inhoud
    texts = content.split('\n')
    file_documents = [Document(page_content=text.strip(), metadata={"source": file_name}) for text in texts if text.strip()]
    documents.extend(file_documents)

print(f"Aantal documenten: {len(documents)}")

# 5. Maak de FAISS-vectorstore
document_texts = [doc.page_content for doc in documents]
vectorstore = FAISS.from_texts(document_texts, embeddings_model)

def retrieve_documents(vraag, k=3):
    """Haal de top k relevante documenten op uit de vectorstore."""
    # Controleer of vectorstore is aangemaakt
    if 'vectorstore' not in globals():
        raise NameError("Vectorstore is niet gedefinieerd. Zorg ervoor dat je FAISS-vectorstore hebt aangemaakt.")

    # Zoek naar relevante documenten
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]

def generate_answer(vraag, context):
    prompt = f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n{context}\n\nVraag: {vraag}\nAntwoord:"
    result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
    return result[0]['generated_text']

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

# einde
if __name__ == "__main__":
    from waitress import serve
    print("Running production server with Waitress...")
    serve(app, host="0.0.0.0", port=5000)