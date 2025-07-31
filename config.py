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
    
    # Configuración Brasilia
    BRASILIA_USERNAME = os.environ.get('BRASILIA_USERNAME') or 'VI_WEB12'
    BRASILIA_PASSWORD = os.environ.get('BRASILIA_PASSWORD') or 'P1NBU52020'
    
    # Configuración Arauca Brasilia (mismo usuario que Brasilia)
    ARAUCA_BRASILIA_USERNAME = os.environ.get('ARAUCA_BRASILIA_USERNAME') or 'VI_WEB12'
    ARAUCA_BRASILIA_PASSWORD = os.environ.get('ARAUCA_BRASILIA_PASSWORD') or 'P1NBU52020'
    
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
        elif service_name.lower() == 'brasilia':
            return {
                'username': Config.BRASILIA_USERNAME,
                'password': Config.BRASILIA_PASSWORD
            }
        elif service_name.lower() == 'arauca_brasilia':
            return {
                'username': Config.ARAUCA_BRASILIA_USERNAME,
                'password': Config.ARAUCA_BRASILIA_PASSWORD
            }
        return {} 