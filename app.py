# Importeer vereiste bibliotheken
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from supabase import create_client, Client
import logging
from memory_profiler import profile

# Logging configureren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuratie voor Supabase
SUPABASE_URL = "https://jrakvtaklrigozchagcr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyYWt2dGFrbHJpZ296Y2hhZ2NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUwNzQ4ODIsImV4cCI6MjA1MDY1MDg4Mn0.gWw2dGI8J-kzbd7SUuFfDFoviNLB39GrTdUpToKonek"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialiseer FastAPI
app = FastAPI()

# Initialiseer modellen
class SentenceTransformerWrapper(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        if not hasattr(self, 'model'):
            self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Genereer embeddings voor een lijst met teksten."""
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        """Genereer een embedding voor een enkele vraag."""
        return self.model.encode([query], show_progress_bar=False)[0]

# Initialiseer embeddings en BLOOMZ-pipeline
@app.on_event("startup")
async def load_models():
    global embeddings_model
    embeddings_model = SentenceTransformerWrapper()

nlp_pipeline = pipeline("text-generation", model="bigscience/bloomz-1b7")

# Functie: FAISS-vectorstore opbouwen vanuit Supabase
@profile
def build_vectorstore_from_supabase():
    try:
        response = supabase.storage().from_('documents').list()
        if not response:
            logger.warning("Geen documenten gevonden in Supabase.")
            return FAISS.from_texts([], embeddings_model)
        documents = []
        for file in response:
            file_content = supabase.storage().from_('documents').download(f"documents/{file['name']}")
            content = file_content.decode('windows-1252')  # Decodeer inhoud
            texts = content.split('\n')
            file_documents = [
                Document(page_content=text.strip(), metadata={"source": file["name"]})
                for text in texts if text.strip()
            ]
            documents.extend(file_documents)
        document_texts = [doc.page_content for doc in documents]
        return FAISS.from_texts(document_texts, embeddings_model)
    except Exception as e:
        logger.error(f"Fout bij opbouwen van vectorstore: {str(e)}")
        raise HTTPException(status_code=500, detail="Fout bij opbouwen van vectorstore.")

# Initialiseer FAISS-vectorstore
vectorstore = build_vectorstore_from_supabase()

# Functie: Relevante documenten ophalen
def retrieve_documents(vraag, k=3):
    if vectorstore is None:
        raise NameError("Vectorstore is niet gedefinieerd. Zorg ervoor dat je FAISS-vectorstore hebt aangemaakt.")
    results = vectorstore.similarity_search(vraag, k=k)
    return [doc.page_content for doc in results]

# Functie: Antwoord genereren
@profile
def generate_answer(vraag, context):
    try:
        prompt = (
            f"Gebruik de volgende context om een nauwkeurig antwoord te formuleren:\n\n"
            f"Context:\n{context}\n\n"
            f"Vraag: {vraag}\n\n"
            f"Antwoord:"
        )
        max_length = min(500, len(context.split()) + 100)
        result = nlp_pipeline(prompt, max_length=max_length, truncation=True, num_return_sequences=1)
        if result and "generated_text" in result[0]:
            return result[0]['generated_text']
        else:
            return "Het model kon geen antwoord genereren."
    except Exception as e:
        logger.error(f"Fout bij antwoordgeneratie: {str(e)}")
        return "Er trad een fout op bij het genereren van het antwoord."

# Functie: Hoofdfunctie voor vraag en antwoord
def kba_antwoord(vraag):
    try:
        relevante_documenten = retrieve_documents(vraag)
        if not relevante_documenten:
            return "Geen relevante documenten gevonden om deze vraag te beantwoorden."
        context = "\n".join(relevante_documenten)
        antwoord = generate_answer(vraag, context)
        logger.info(f"Gegenereerd antwoord: {antwoord}")
        return antwoord
    except Exception as e:
        logger.error(f"Fout in kba_antwoord: {str(e)}")
        return "Er trad een fout op bij het verwerken van de vraag."

# FastAPI Endpoints
@app.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...), token: str = Header(...)):
    if token != "jouw-geheime-token":
        raise HTTPException(status_code=403, detail="Ongeldig API-token")
    for file in files:
        try:
            response = supabase.storage().from_('documents').upload(
                f"documents/{file.filename}", file.file
            )
            if "error" in response:
                raise HTTPException(
                    status_code=500,
                    detail=f"Fout bij uploaden van {file.filename}: {response['error']['message']}"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fout bij uploaden: {str(e)}")
    return {"status": "success", "message": f"{len(files)} bestanden succesvol geupload."}

@app.delete("/documents/")
async def delete_document(filename: str, token: str = Header(...)):
    if token != "jouw-geheime-token":
        raise HTTPException(status_code=403, detail="Ongeldig API-token")
    try:
        existing_files = supabase.storage().from_('documents').list()
        if filename not in [file['name'] for file in existing_files]:
            raise HTTPException(status_code=404, detail=f"Bestand '{filename}' niet gevonden.")
        response = supabase.storage().from_('documents').remove([f"documents/{filename}"])
        if "error" in response:
            raise HTTPException(status_code=500, detail=f"Fout bij verwijderen: {response['error']['message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij verwijderen: {str(e)}")
    return {"status": "success", "message": f"Document '{filename}' succesvol verwijderd."}

@app.get("/documents/")
async def list_documents():
    try:
        response = supabase.storage().from_('documents').list()
        if not response:
            return {"status": "success", "documents": [], "message": "Geen documenten gevonden."}
        documents = [
            {
                "name": file["name"],
                "size": file.get("size", "Onbekend"),
                "created_at": file.get("created_at", "Onbekend"),
            }
            for file in response
        ]
        return {"status": "success", "documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij ophalen documenten: {str(e)}")

# Debug: Testvraag
if __name__ == "__main__":
    vraag = "Wat moet ik doen met bedrijfsapparatuur?"
    antwoord = kba_antwoord(vraag)
    print(f"EINDE DEBUG antwoord:\n{antwoord}")