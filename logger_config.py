import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # Configurar el logger principal
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Logger para errores
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Logger para acceso
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)
    
    # Configurar los loggers en la aplicación
    app.logger.addHandler(error_handler)
    app.logger.addHandler(access_handler)
    app.logger.setLevel(logging.INFO)
    
    return app.logger
