from flask import Blueprint, request, jsonify

# Blueprint aanmaken
kba_blueprint = Blueprint('kba', __name__)

# Endpoint om vragen te beantwoorden
@kba_blueprint.route("/", methods=["POST"])
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
@kba_blueprint.route("/", methods=["OPTIONS"])
def handle_options():
    response = jsonify()
    response.headers.add("Access-Control-Allow-Origin", "https://yininit.nl")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response, 204