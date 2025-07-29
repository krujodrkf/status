from flask import Flask, render_template, jsonify
import os
import json
import threading
import time
from datetime import datetime, timedelta
import schedule
from services.bolivariano import BolivarianoService
from config import Config
from database import MonitoringDatabase

app = Flask(__name__)
app.config.from_object(Config)

# Base de datos para almacenamiento persistente
db = MonitoringDatabase()

# Servicios disponibles
services = {
    'bolivariano': BolivarianoService()
}

def run_service_check(service_name, service):
    """Ejecuta la verificación de un servicio y almacena el resultado"""
    now = datetime.now()
    result = service.check_service()
    
    # Crear clave para el tiempo (redondeado a 5 minutos)
    time_key = now.replace(second=0, microsecond=0)
    time_key = time_key.replace(minute=(time_key.minute // 5) * 5)
    time_str = time_key.strftime('%H:%M')
    
    # Guardar en base de datos
    db.insert_monitoring_data(
        service_name=service_name,
        timestamp=now,
        time_slot=time_str,
        status=result['status'],
        request_data=result.get('request', ''),
        response_data=result.get('response', ''),
        error_message=result.get('error', '')
    )
    
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {service_name}: {result['status']}")

def run_all_checks():
    """Ejecuta verificaciones para todos los servicios"""
    for service_name, service in services.items():
        try:
            run_service_check(service_name, service)
        except Exception as e:
            print(f"Error checking {service_name}: {str(e)}")

def cleanup_old_data():
    """Limpia datos antiguos de la base de datos"""
    try:
        deleted_count = db.cleanup_old_data(hours_to_keep=48)
        if deleted_count > 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Limpieza: eliminados {deleted_count} registros antiguos")
    except Exception as e:
        print(f"Error en limpieza de datos: {str(e)}")

def start_scheduler():
    """Inicia el scheduler en un hilo separado"""
    schedule.every(5).minutes.do(run_all_checks)
    schedule.every(6).hours.do(cleanup_old_data)
    
    # Ejecutar verificaciones y limpieza inicial
    run_all_checks()
    cleanup_old_data()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', services=list(services.keys()))

@app.route('/api/data/<service_name>')
def get_service_data(service_name):
    """API endpoint para obtener datos de un servicio específico"""
    if service_name not in services:
        return jsonify({'error': 'Service not found'}), 404
    
    data = db.get_service_data_last_24h(service_name)
    return jsonify(data)

@app.route('/api/data')
def get_all_data():
    """API endpoint para obtener datos de todos los servicios"""
    return jsonify(db.get_all_services_data_last_24h())

@app.route('/api/stats')
def get_database_stats():
    """API endpoint para obtener estadísticas de la base de datos"""
    return jsonify(db.get_database_stats())

if __name__ == '__main__':
    # Iniciar el scheduler en un hilo separado
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 