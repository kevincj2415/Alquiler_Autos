import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_default')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/default')
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY', 'demo-key')