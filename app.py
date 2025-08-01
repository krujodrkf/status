from flask import Flask, render_template, jsonify
import os
import json
import threading
import time
from datetime import datetime, timedelta
import schedule
from services.bolivariano import BolivarianoService
from services.brasilia import BrasiliaService
from services.arauca_brasilia import AraucaBrasiliaService
from services.transpurificacion import TranspurificacionService
from config import Config
from database import MonitoringDatabase

app = Flask(__name__)
app.config.from_object(Config)

# Registrar filtro personalizado para formatear nombres de servicios
app.jinja_env.filters['format_service_name'] = lambda service_name: service_name.replace('_', ' ').title()

# Base de datos para almacenamiento persistente
db = MonitoringDatabase()

# Servicios disponibles con sus intervalos de consulta (en minutos)
services = {
    'bolivariano': BolivarianoService(),
    'brasilia': BrasiliaService(),
    'arauca_brasilia': AraucaBrasiliaService(),
    'transpurificacion': TranspurificacionService()
}

# Intervalos de consulta por servicio (en minutos)
service_intervals = {
    'bolivariano': 5,
    'brasilia': 10,
    'arauca_brasilia': 5,
    'transpurificacion': 5
}

# Control de ejecuciones para evitar duplicados
last_execution = {}

def run_service_check(service_name, service):
    """Ejecuta la verificación de un servicio y almacena el resultado"""
    now = datetime.now()
    
    # Control anti-duplicados: evitar múltiples ejecuciones en el mismo minuto
    current_minute = now.replace(second=0, microsecond=0)
    last_exec = last_execution.get(service_name)
    
    if last_exec and (current_minute - last_exec).total_seconds() < 60:
        print(f"[DEBUG] SALTANDO {service_name} - ya ejecutado en este minuto")
        return
    
    last_execution[service_name] = current_minute
    print(f"[DEBUG] EJECUTANDO verificación completa para {service_name}")
    result = service.check_service()
    
    # Crear clave para el tiempo (redondeado a 5 minutos)
    time_key = now.replace(second=0, microsecond=0)
    time_key = time_key.replace(minute=(time_key.minute // 5) * 5)
    time_str = time_key.strftime('%H:%M')
    
    # Calcular cuántas barras debe pintar según el intervalo del servicio
    service_interval = service_intervals.get(service_name, 5)
    bars_to_paint = service_interval // 5  # Cada barra representa 5 minutos
    
    # Guardar en base de datos múltiples registros para barras consecutivas
    for i in range(bars_to_paint):
        # Calcular time_slot para cada barra
        current_time_key = time_key + timedelta(minutes=i * 5)
        current_time_str = current_time_key.strftime('%H:%M')
        
        db.insert_monitoring_data(
            service_name=service_name,
            timestamp=now,
            time_slot=current_time_str,
            status=result['status'],
            request_data=result.get('request', ''),
            response_data=result.get('response', ''),
            error_message=result.get('error', '')
        )
    
    # Mensaje más descriptivo según el resultado
    if result['status'] == 'success':
        bars_info = f"({bars_to_paint} barras)" if bars_to_paint > 1 else ""
        status_msg = f"✅ COMPLETE (Login + Request OK) {bars_info}"
    else:
        error_preview = result.get('error', 'Unknown error')[:50] + '...' if len(result.get('error', '')) > 50 else result.get('error', 'Unknown error')
        status_msg = f"❌ FAILED: {error_preview}"
    
    print(f"[{now.strftime('%H:%M:%S')}] {service_name.upper()}: {status_msg}")

def run_individual_service_check(service_name):
    """Ejecuta verificación para un servicio específico"""
    try:
        service = services[service_name]
        run_service_check(service_name, service)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {service_name.upper()}: ❌ EXCEPTION - {str(e)}")

def cleanup_old_data():
    """Limpia datos antiguos de la base de datos"""
    try:
        deleted_count = db.cleanup_old_data(hours_to_keep=24)
        if deleted_count > 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Limpieza: eliminados {deleted_count} registros antiguos")
    except Exception as e:
        print(f"Error en limpieza de datos: {str(e)}")

def start_scheduler():
    """Inicia el scheduler en un hilo separado"""
    print("\n🚀 INICIANDO MONITOR DE SERVICIOS")
    print("=" * 50)
    
    # Programar cada servicio con su intervalo específico
    print("📅 Programando servicios:")
    for service_name, interval_minutes in service_intervals.items():
        schedule.every(interval_minutes).minutes.do(run_individual_service_check, service_name)
        formatted_name = service_name.replace('_', ' ').title()
        print(f"   • {formatted_name}: cada {interval_minutes} min.")
    
    # Programar limpieza de datos
    schedule.every(1).hours.do(cleanup_old_data)
    print(f"   • Limpieza BD: cada 1 hora")
    
    # Ejecutar verificaciones iniciales para todos los servicios
    print(f"\n🔍 VERIFICACIÓN INICIAL ({len(services)} servicios):")
    print("-" * 30)
    for service_name in services.keys():
        run_individual_service_check(service_name)
    cleanup_old_data()
    
    print("\n✅ Sistema iniciado correctamente")
    print("📊 Monitoreo automático activo...")
    print("=" * 50)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    """Página principal"""
    # Crear lista de servicios con sus intervalos para el template
    services_with_intervals = []
    for service_name in sorted(services.keys()):
        services_with_intervals.append({
            'name': service_name,
            'interval': service_intervals[service_name]
        })
    
    return render_template('index.html', 
                         services=sorted(services.keys()),
                         services_with_intervals=services_with_intervals)

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