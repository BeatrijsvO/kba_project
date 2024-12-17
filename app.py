from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Sta verzoeken van andere domeinen toe

@app.route("/kba", methods=["POST"])  # Zorg ervoor dat alleen POST wordt toegestaan
def answer_question():
    # Controleer of er JSON is verzonden
    if not request.is_json:
        return jsonify({"error": "Verwacht JSON-data"}), 400

    # Haal de vraag uit het verzoek
    data = request.get_json()
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400

    # Verwerk de vraag en genereer een antwoord
    antwoord = f"Hier is je antwoord op: '{vraag}'"
    return jsonify({"vraag": vraag, "antwoord": antwoord})

if __name__ == "__main__":
    from waitress import serve
    print("Running in production with Waitress...")
    serve(app, host="0.0.0.0", port=5000)