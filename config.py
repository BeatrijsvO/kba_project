class Config:
    """Configuratie voor de applicatie."""
    APP_NAME = "KBA Webservice"
    DEBUG = True
    PORT = 10000  # Standaardpoort voor de applicatie
    HOST = "0.0.0.0"  # Luisteren op alle netwerken
    CORS_ORIGINS = ["https://yininit.nl"]  # Toegestane origins