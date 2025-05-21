"""
Configuración para el entorno de desarrollo
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración básica
DEBUG = True
TESTING = False
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')

# Configuración de la base de datos
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/alquiler_coches')

# Configuración de caché
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Configuración de archivos
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = os.path.join('frontend', 'static', 'uploads', 'cars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Configuración de logging
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
LOG_DIR = 'logs'

# Configuración de seguridad
SESSION_COOKIE_SECURE = False  # Set to True in production
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

# Configuración de CORS
CORS_ORIGINS = ['http://localhost:5700']
