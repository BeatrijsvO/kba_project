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
@app.route("/kba", methods=["POST"])
def answer_question():
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    data = request.get_json()
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    antwoord = f"Hier is je antwoord op: '{vraag}'"
    return jsonify({"vraag": vraag, "antwoord": antwoord})

# OPTIONS-handler om preflight-verzoeken correct af te handelen
@app.route("/kba", methods=["OPTIONS"])
def handle_options():
    response = jsonify()
    response.headers.add("Access-Control-Allow-Origin", Config.CORS_ORIGINS[0])
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response, 204

# Start de server met Waitress
if __name__ == "__main__":
    from waitress import serve
    import os
    print("Running production server with Waitress...")
    port = int(os.getenv("PORT", Config.PORT))
    serve(app, host=Config.HOST, port=port)