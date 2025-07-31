import sqlite3
import os
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

class MonitoringDatabase:
    def __init__(self, db_path: str = 'monitoring.db'):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Crea las tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    time_slot TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service_name, time_slot, timestamp)
                )
            ''')
            
            # Crear índices para mejorar rendimiento
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_service_timestamp 
                ON monitoring_data(service_name, timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON monitoring_data(timestamp)
            ''')
            
            conn.commit()
    
    def insert_monitoring_data(self, service_name: str, timestamp: datetime, 
                              time_slot: str, status: str, request_data: str = '', 
                              response_data: str = '', error_message: str = ''):
        """Inserta o actualiza datos de monitoreo"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO monitoring_data 
                (service_name, timestamp, time_slot, status, request_data, response_data, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (service_name, timestamp, time_slot, status, request_data, response_data, error_message))
            conn.commit()
    
    def get_service_data_last_24h(self, service_name: str) -> Dict[str, Dict]:
        """Obtiene datos de un servicio de las últimas 24 horas"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT time_slot, timestamp, status, request_data, response_data, error_message
                FROM monitoring_data 
                WHERE service_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (service_name, cutoff_time))
            
            result = {}
            for row in cursor:
                # Usar el time_slot más reciente si hay duplicados
                if row['time_slot'] not in result:
                    result[row['time_slot']] = {
                        'timestamp': row['timestamp'],
                        'status': row['status'],
                        'request': row['request_data'] or '',
                        'response': row['response_data'] or '',
                        'error': row['error_message'] or ''
                    }
            
            return result
    
    def get_all_services_data_last_24h(self) -> Dict[str, Dict]:
        """Obtiene datos de todos los servicios de las últimas 24 horas"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT service_name, time_slot, timestamp, status, request_data, response_data, error_message
                FROM monitoring_data 
                WHERE timestamp >= ?
                ORDER BY service_name, timestamp DESC
            ''', (cutoff_time,))
            
            result = {}
            for row in cursor:
                service_name = row['service_name']
                if service_name not in result:
                    result[service_name] = {}
                
                # Usar el time_slot más reciente si hay duplicados
                if row['time_slot'] not in result[service_name]:
                    result[service_name][row['time_slot']] = {
                        'timestamp': row['timestamp'],
                        'status': row['status'],
                        'request': row['request_data'] or '',
                        'response': row['response_data'] or '',
                        'error': row['error_message'] or ''
                    }
            
            return result
    
    def cleanup_old_data(self, hours_to_keep: int = 24):
        """Elimina datos más antiguos del tiempo especificado"""
        cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM monitoring_data 
                WHERE timestamp < ?
            ''', (cutoff_time,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    def get_database_stats(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Total de registros
            total_records = conn.execute('SELECT COUNT(*) as count FROM monitoring_data').fetchone()['count']
            
            # Registros por servicio
            services_cursor = conn.execute('''
                SELECT service_name, COUNT(*) as count, 
                       MIN(timestamp) as oldest, 
                       MAX(timestamp) as newest
                FROM monitoring_data 
                GROUP BY service_name
            ''')
            
            services_stats = {}
            for row in services_cursor:
                services_stats[row['service_name']] = {
                    'total_records': row['count'],
                    'oldest_record': row['oldest'],
                    'newest_record': row['newest']
                }
            
            # Tamaño del archivo de base de datos
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'total_records': total_records,
                'services': services_stats,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2)
            }
    
    def migrate_from_memory_data(self, memory_data: Dict):
        """Migra datos existentes en memoria a la base de datos"""
        migrated_count = 0
        
        for service_name, service_data in memory_data.items():
            for time_slot, data in service_data.items():
                try:
                    # Intentar parsear el timestamp existente
                    if 'timestamp' in data:
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    else:
                        # Si no hay timestamp, usar fecha actual con la hora del time_slot
                        now = datetime.now()
                        hour, minute = map(int, time_slot.split(':'))
                        timestamp = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    self.insert_monitoring_data(
                        service_name=service_name,
                        timestamp=timestamp,
                        time_slot=time_slot,
                        status=data.get('status', 'unknown'),
                        request_data=data.get('request', ''),
                        response_data=data.get('response', ''),
                        error_message=data.get('error', '')
                    )
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Error migrando datos para {service_name} {time_slot}: {e}")
                    continue
        
        return migrated_count 