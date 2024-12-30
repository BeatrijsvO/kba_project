import os

class Config:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # Of specificeer je domein
    SECRET_KEY = os.getenv("SECRET_KEY")
    SUPABASE_URL= os.getenv("SECRET_KEY")
    SUPABASE_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", False)