from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Sta verzoeken toe vanaf andere domeinen

@app.route("/kba", methods=["POST"])
def answer_question():
    data = request.json
    vraag = data.get("vraag", "")
    if not vraag:
        return jsonify({"error": "Geen vraag ontvangen."}), 400
    
    antwoord = f"Hier is je antwoord op: '{vraag}'"
    return jsonify({"vraag": vraag, "antwoord": antwoord})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)