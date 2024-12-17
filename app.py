
# Deze code combineert document retrieval via een FAISS-vectorstore
#  en antwoordgeneratie via Flan-T5.

# Stap 1: Importeer vereiste bibliotheken
!pip install -U langchain sentence-transformers faiss-cpu langchain-community

from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from transformers import pipeline
from google.colab import files


# andere app !!!!
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Sta verzoeken van andere domeinen toe

@app.route("/kba", methods=["POST"])



def answer_question():
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag1 = data.get("vraag1", "")
    if not vraag1:
        return jsonify({"error": "Geen vraag1 ontvangen."}), 400

    antwoord1 = f"Hier is je antwoord1 op: '{vraag1}'"
    return jsonify({"vraag1": vraag1, "antwoord1": antwoord1})




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

# 3. Initialiseer Flan-T5 model pipeline
#nlp_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
# Gebruik BLOOMZ als krachtiger model
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



# 6. Functie voor ophalen van relevante documenten
#def retrieve_documents(vraag, k=3):
#    results = vectorstore.similarity_search(vraag, k=k)
#    return [result.page_content for result in results]


def retrieve_documents(vraag, k=3):
    """Haal de top k relevante documenten op uit de vectorstore."""
    # Controleer of vectorstore is aangemaakt
    if 'vectorstore' not in globals():
        raise NameError("Vectorstore is niet gedefinieerd. Zorg ervoor dat je FAISS-vectorstore hebt aangemaakt.")

    # Zoek naar relevante documenten
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]



# 7. Functie voor antwoord genereren met BLOOMZ

# NEW
#def generate_answer(vraag, context):
#    prompt = (
#        f"Gebruik alleen de relevante informatie uit onderstaande tekst om de vraag te beantwoorden:\n"
#        f"{context}\n\n"
#        f"Vraag: {vraag}\n"
#        f"Antwoord (alleen waar lunchpauze in voorkomt):"
#    )
#    print(f"DEBUG CONTEXTTTTTT:\n{context}")

# ORG
def generate_answer(vraag, context):

    prompt = (
        f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
        f"{context}\n\n"
        f"Vraag: {vraag}\n"
        f"Antwoord (geef alleen het relevante deel van de context):"
    )


    #prompt = f"Gebruik de onderstaande informatie om de vraag te beantwoorden:{context}\n\nVraag: {vraag}\nAntwoord (geef alleen het relevante deel van de context):"

    #prompt = f"Context: {context}\n\nVraag: {vraag}\nAntwoord:"

    print(f"DEBUG Prompt:\n{prompt}")  # Debugging
    result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
    print(f"DEBUG Result:\n{result}")  # Debugging
    print(f"DEBUG Result[0] Generated tekst:\n{result[0]['generated_text']}")  # Debugging
    return result[0]['generated_text']



# OPTIE 1 Filter de context!! Hoort bij: 8. Hoofdfunctie: Vraag en antwoord

#def filter_context(context, vraag):
 #   """Filter de context op basis van trefwoorden in de vraag."""
 #   vraag_trefwoorden = [woord.lower() for woord in vraag.split()]  # Vraag splitsen in trefwoorden
 #   relevante_zinnen = []
 #   for zin in context.split('\n'):
 #       # Voeg zinnen toe die een overlap hebben met trefwoorden in de vraag
 #       if any(trefwoord in zin.lower() for trefwoord in vraag_trefwoorden):
 #           relevante_zinnen.append(zin)
 #   return "\n".join(relevante_zinnen)



# 8. Hoofdfunctie: Vraag en antwoord

def kba_antwoord(vraag):
    relevante_documenten = retrieve_documents(vraag)
    context = "\n".join(relevante_documenten)

  # OPTIE 1 Filter de context !!
    #gefilterde_context = filter_context(context, vraag)
    #if not gefilterde_context:
    #    return "Geen relevante informatie gevonden om deze vraag te beantwoorden."
    #print(f"Gefilterde context:\n{filter_context(context, vraag)}")
    #antwoord = generate_answer(vraag, gefilterde_context)

  # OPTIE 2 Origineel
    antwoord = generate_answer(vraag, context)

    print(f"DEBUG Gevonden documenten:\n{relevante_documenten}")
    print(f"DEBUG antwoord in kba_antwoord:\n{antwoord}")

    return antwoord


# Testvraag
#vraag = "Wat moet ik doen met bedrijfsapparatuur?"
vraag = "Hoe laat is het lunchpauze?"
antwoord = kba_antwoord(vraag)
print(f"EINDE DEBUG antwoord:\n{antwoord}")

#print(f"Vraag : {vraag}")






if __name__ == "__main__":
    from waitress import serve
    print("Running production server with Waitress...")
    serve(app, host="0.0.0.0", port=5000)