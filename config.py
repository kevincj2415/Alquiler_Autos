import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'kevin_jairo')  # Fallback para mantener compatibilidad
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/alquiler_coches')
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY', '47289007-1c84d3d414f613c857c6ded8f')
