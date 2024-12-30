from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config

# Flask-app configuratie
app = Flask(__name__)

# Laad configuratie vanuit config.py
app.config.from_object(Config)

# CORS-configuratie
CORS(app, resources={r"/kba": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

# Endpoint om vragen te beantwoorden

@app.route("/")
def home():
    return "Webservice draait correct!"

@app.route("/kba", methods=["POST"])
def answer_question():
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    # Pas het antwoord aan
    antwoord = f"Bedankt voor je vraag: '{vraag}'. Hier is een aangepast antwoord!"
    return jsonify({"vraag": vraag, "antwoord": antwoord})
