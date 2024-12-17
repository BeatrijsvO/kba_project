from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask-app configuratie
app = Flask(__name__)
CORS(app)  # Sta CORS toe voor API-aanroepen

# Root route to test if the service is running
@app.route('/', methods=['GET'])
def home():
    # Return a simple JSON response to confirm the service is active
    return jsonify({
        "message": "Webservice is actief!"
    })

# A simple test route with POST method
@app.route('/test', methods=['POST'])
def test_route():
    # Extract JSON data from the request
    data = request.json  # Expecting JSON input
    name = data.get("name", "onbekend")  # Default value if 'name' is missing
    # Return a personalized response
    return jsonify({
        "message": f"Hallo, {name}! De webservice werkt prima."
    })

if __name__ == '__main__':
    # Run the Flask app with debugging enabled
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )