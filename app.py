from flask import Flask
from flask_cors import CORS
from services.kba.endpoints import kba_blueprint  # Importeer de Blueprint

# Flask-app configuratie
app = Flask(__name__)

# CORS-configuratie: Sta verzoeken toe van specifieke origin (jouw frontend)
CORS(app, resources={r"/api/kba/*": {"origins": ["https://yininit.nl"]}}, supports_credentials=True)

# Registreer de Blueprint
app.register_blueprint(kba_blueprint, url_prefix="/api/kba")

# Start de server met Waitress
if __name__ == "__main__":
    from waitress import serve
    import os
    print("Running production server with Waitress...")
    port = int(os.environ.get("PORT", 5000))  # Dynamische poort ophalen
    serve(app, host="0.0.0.0", port=port)