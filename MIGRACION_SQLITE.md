# 🗄️ Migración a SQLite - Status Monitor

## 📋 ¿Qué cambió?

El sistema ahora usa **SQLite** en lugar de almacenamiento en memoria para una mejor gestión de datos:

### ✅ **Ventajas del nuevo sistema:**

1. **Persistencia**: Los datos NO se pierden al reiniciar la aplicación
2. **Rotación automática**: Limpia datos antiguos automáticamente (mantiene 48 horas)
3. **Mejor organización**: Separación correcta por fecha y hora
4. **Estadísticas**: Nueva API para ver uso de la base de datos
5. **Escalabilidad**: Soporte para grandes volúmenes de datos

## 🔧 **Archivos nuevos/modificados:**

### **Nuevos archivos:**
- `database.py` - Módulo de gestión de base de datos SQLite
- `test_database.py` - Script de prueba de funcionalidad
- `MIGRACION_SQLITE.md` - Esta documentación

### **Archivos modificados:**
- `app.py` - Integración con SQLite y limpieza automática
- `.gitignore` - Exclusión de archivos .db

## 🏗️ **Estructura de la base de datos:**

### **Tabla: monitoring_data**
```sql
CREATE TABLE monitoring_data (
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
);
```

### **Índices para rendimiento:**
- `idx_service_timestamp`: Para consultas por servicio y fecha
- `idx_timestamp`: Para consultas generales por fecha

## 🚀 **Nuevas funcionalidades:**

### **1. API de estadísticas:**
```
GET /api/stats
```
Devuelve información sobre la base de datos:
- Total de registros
- Tamaño del archivo
- Estadísticas por servicio

### **2. Limpieza automática:**
- Se ejecuta cada **6 horas**
- Elimina datos más antiguos de **48 horas**
- Mantiene la base de datos optimizada

### **3. Consultas optimizadas:**
- Solo muestra datos de las **últimas 24 horas**
- Consultas más rápidas con índices
- Manejo de duplicados mejorado

## 🔧 **Cómo probar la migración:**

### **1. Ejecutar pruebas:**
```bash
python test_database.py
```

### **2. Ver estadísticas de producción:**
```bash
python -c "from database import MonitoringDatabase; db = MonitoringDatabase(); print(db.get_database_stats())"
```

### **3. Verificar archivo de base de datos:**
```bash
ls -la monitoring.db
```

## 🕒 **Gestión de datos por tiempo:**

### **Antes (memoria):**
❌ Datos se acumulaban sin límite  
❌ Se perdían al reiniciar  
❌ Sin separación por fecha  
❌ Posible overflow de memoria  

### **Ahora (SQLite):**
✅ Limpieza automática cada 6 horas  
✅ Persistencia entre reinicios  
✅ Separación correcta por timestamp  
✅ Uso controlado de espacio  

## 🔄 **Migración automática:**

La aplicación maneja automáticamente:

1. **Creación de tablas** al primer arranque
2. **Migración de datos** en memoria (si los hay)
3. **Compatibilidad** con la interfaz web existente
4. **Limpieza inicial** de datos antiguos

## 📊 **Monitoreo del sistema:**

### **Comandos útiles:**

```bash
# Ver tamaño de la base de datos
ls -lh monitoring.db

# Contar registros totales
sqlite3 monitoring.db "SELECT COUNT(*) FROM monitoring_data;"

# Ver servicios únicos
sqlite3 monitoring.db "SELECT DISTINCT service_name FROM monitoring_data;"

# Ver datos más recientes
sqlite3 monitoring.db "SELECT * FROM monitoring_data ORDER BY timestamp DESC LIMIT 10;"
```

## ⚠️ **Notas importantes:**

### **Backup recomendado:**
```bash
# Hacer backup de la base de datos
cp monitoring.db monitoring_backup_$(date +%Y%m%d).db
```

### **Ubicación del archivo:**
- El archivo `monitoring.db` se crea en el directorio del proyecto
- Está excluido del control de versiones (`.gitignore`)
- Se puede mover o copiar libremente

### **Recuperación:**
Si se corrompe la base de datos, simplemente elimínala:
```bash
rm monitoring.db
```
La aplicación recreará automáticamente una nueva al reiniciar.

## 🎯 **Resultado final:**

- ✅ **Sin pérdida de datos** entre reinicios
- ✅ **Gestión automática** de espacio
- ✅ **Compatibilidad completa** con la interfaz web
- ✅ **Mejor rendimiento** en consultas
- ✅ **Escalabilidad** para múltiples servicios

El sistema ahora es **robusto** y **listo para producción** 🚀 