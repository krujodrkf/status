#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de la base de datos SQLite
"""

import json
from datetime import datetime, timedelta
from database import MonitoringDatabase

def test_database():
    """Prueba las funciones principales de la base de datos"""
    print("🔍 Probando base de datos SQLite...")
    
    # Crear instancia de base de datos
    db = MonitoringDatabase('test_monitoring.db')
    
    # Test 1: Insertar datos de prueba
    print("\n📝 Test 1: Insertando datos de prueba...")
    
    now = datetime.now()
    test_data = [
        {
            'service_name': 'bolivariano',
            'timestamp': now - timedelta(minutes=10),
            'time_slot': '14:20',
            'status': 'success',
            'request_data': '{"test": "request"}',
            'response_data': '{"test": "response"}',
            'error_message': ''
        },
        {
            'service_name': 'bolivariano',
            'timestamp': now - timedelta(minutes=5),
            'time_slot': '14:25',
            'status': 'error',
            'request_data': '{"test": "request2"}',
            'response_data': '',
            'error_message': 'Error de prueba'
        },
        {
            'service_name': 'test_service',
            'timestamp': now,
            'time_slot': '14:30',
            'status': 'success',
            'request_data': '{"test": "request3"}',
            'response_data': '{"test": "response3"}',
            'error_message': ''
        }
    ]
    
    for data in test_data:
        db.insert_monitoring_data(**data)
        print(f"  ✅ Insertado: {data['service_name']} {data['time_slot']} {data['status']}")
    
    # Test 2: Consultar datos de un servicio
    print("\n📊 Test 2: Consultando datos de 'bolivariano'...")
    bolivariano_data = db.get_service_data_last_24h('bolivariano')
    print(f"  📈 Datos encontrados: {len(bolivariano_data)} registros")
    for time_slot, data in bolivariano_data.items():
        print(f"    {time_slot}: {data['status']}")
    
    # Test 3: Consultar todos los servicios
    print("\n📊 Test 3: Consultando todos los servicios...")
    all_data = db.get_all_services_data_last_24h()
    print(f"  📈 Servicios encontrados: {list(all_data.keys())}")
    for service_name, service_data in all_data.items():
        print(f"    {service_name}: {len(service_data)} registros")
    
    # Test 4: Estadísticas de la base de datos
    print("\n📊 Test 4: Estadísticas de la base de datos...")
    stats = db.get_database_stats()
    print(f"  📈 Total de registros: {stats['total_records']}")
    print(f"  💾 Tamaño de BD: {stats['database_size_mb']} MB")
    print(f"  🏷️  Servicios:")
    for service_name, service_stats in stats['services'].items():
        print(f"    {service_name}: {service_stats['total_records']} registros")
    
    # Test 5: Limpieza de datos antiguos
    print("\n🧹 Test 5: Probando limpieza de datos antiguos...")
    # Insertar datos muy antiguos
    old_timestamp = now - timedelta(hours=50)
    db.insert_monitoring_data(
        service_name='old_service',
        timestamp=old_timestamp,
        time_slot='10:00',
        status='success',
        request_data='{"old": "data"}',
        response_data='{"old": "response"}',
        error_message=''
    )
    
    print(f"  📝 Insertado dato antiguo: {old_timestamp}")
    
    # Verificar que se insertó
    stats_before = db.get_database_stats()
    print(f"  📊 Registros antes de limpieza: {stats_before['total_records']}")
    
    # Limpiar datos antiguos (mantener solo 24 horas)
    deleted_count = db.cleanup_old_data(hours_to_keep=24)
    print(f"  🗑️  Registros eliminados: {deleted_count}")
    
    # Verificar después de limpieza
    stats_after = db.get_database_stats()
    print(f"  📊 Registros después de limpieza: {stats_after['total_records']}")
    
    print("\n✅ Todos los tests completados exitosamente!")
    
    # Limpiar archivo de prueba
    import os
    if os.path.exists('test_monitoring.db'):
        os.remove('test_monitoring.db')
        print("🧹 Archivo de prueba eliminado")

def show_production_stats():
    """Muestra estadísticas de la base de datos de producción"""
    print("\n📊 ESTADÍSTICAS DE BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 50)
    
    # Usar la base de datos de producción
    db = MonitoringDatabase('monitoring.db')
    
    try:
        stats = db.get_database_stats()
        
        print(f"📈 Total de registros: {stats['total_records']}")
        print(f"💾 Tamaño de archivo: {stats['database_size_mb']} MB")
        print(f"📁 Ubicación: {db.db_path}")
        
        if stats['services']:
            print(f"\n🏷️  SERVICIOS ({len(stats['services'])}):")
            for service_name, service_stats in stats['services'].items():
                print(f"  📌 {service_name}:")
                print(f"     Registros: {service_stats['total_records']}")
                print(f"     Más antiguo: {service_stats['oldest_record']}")
                print(f"     Más reciente: {service_stats['newest_record']}")
        else:
            print("\n⚠️  No hay datos en la base de datos")
            
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")

if __name__ == '__main__':
    print("🔧 PRUEBA DE BASE DE DATOS SQLITE")
    print("=" * 40)
    
    # Ejecutar tests
    test_database()
    
    # Mostrar estadísticas de producción
    show_production_stats() 