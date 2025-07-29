import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Configuración Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Configuración Bolivariano
    BOLIVARIANO_USERNAME = os.environ.get('BOLIVARIANO_USERNAME') or 'PBUS@43607'
    BOLIVARIANO_PASSWORD = os.environ.get('BOLIVARIANO_PASSWORD') or 'dpUhwsa#k@'
    
    # Configuración de monitoreo
    CHECK_INTERVAL_MINUTES = 5
    UPDATE_INTERVAL_SECONDS = 30
    
    @staticmethod
    def get_service_config(service_name):
        """Obtiene la configuración de un servicio específico"""
        if service_name.lower() == 'bolivariano':
            return {
                'username': Config.BOLIVARIANO_USERNAME,
                'password': Config.BOLIVARIANO_PASSWORD
            }
        return {} 