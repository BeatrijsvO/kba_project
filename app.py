from flask import Flask
from flask_cors import CORS
from config import Config
from routes.kba import kba_blueprint
import os
from waitress import serve

def create_app():
    """Initialiseer en configureer de Flask-applicatie."""
    app = Flask(__name__)

    # Laad configuratie
    app.config.from_object(Config)

    # Configureer CORS
    CORS(app, resources={r"/kba": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

    # Registreer Blueprints
    app.register_blueprint(kba_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", Config.PORT))
    print("Running production server with Waitress...")
    serve(app, host=Config.HOST, port=port)