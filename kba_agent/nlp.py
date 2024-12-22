from transformers import pipeline

class NLPEngine:
    def __init__(self, model_name="bigscience/bloomz-1b7"):
        self.nlp_pipeline = pipeline("text-generation", model=model_name)

    def generate_answer(self, vraag, context):
        """Genereer een antwoord op basis van de context en vraag."""
        prompt = (
            f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
            f"{context}\n\n"
            f"Vraag: {vraag}\n"
            f"Antwoord (geef alleen het relevante deel van de context):"
        )

        result = self.nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
        return result[0]['generated_text']