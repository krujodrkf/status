# 🐧 Instalación Completa en Ubuntu

## 📋 Guía paso a paso para instalar y configurar como servicio del sistema

### 1️⃣ **Preparar el sistema**

```bash
# Actualizar Ubuntu
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install python3 python3-pip python3-venv git -y
```

### 2️⃣ **Configurar el proyecto**

```bash
# Navegar al directorio del proyecto
cd /ruta/a/tu/proyecto/status

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt
```

### 3️⃣ **Configurar credenciales**

```bash
# Crear archivo .env
nano .env
```

**Contenido del .env:**
```
# Configuración del servicio Bolivariano
BOLIVARIANO_USERNAME=PBUS@43607
BOLIVARIANO_PASSWORD=dpUhwsa#k@

# Configuración de la aplicación
FLASK_ENV=production
SECRET_KEY=cambia_esta_clave_secreta_por_una_real
```

### 4️⃣ **Instalación automática como servicio**

```bash
# Dar permisos de ejecución a los scripts
chmod +x instalar_servicio.sh
chmod +x desinstalar_servicio.sh

# Instalar como servicio del sistema
./instalar_servicio.sh
```

## 🎉 **¡Ya está instalado!**

La aplicación ahora:
- ✅ Se ejecuta automáticamente al iniciar Ubuntu
- ✅ Se reinicia automáticamente si falla
- ✅ Está disponible 24/7
- ✅ Registra logs del sistema

## 📊 **Verificar instalación**

```bash
# Ver estado del servicio
sudo systemctl status status-monitor

# Ver logs
sudo journalctl -u status-monitor -f

# Encontrar tu IP
hostname -I
```

**Acceder desde cualquier dispositivo en tu red:**
- `http://[IP_DE_UBUNTU]:5000`

## 🛠️ **Comandos útiles**

### **Control del servicio:**
```bash
sudo systemctl start status-monitor      # Iniciar
sudo systemctl stop status-monitor       # Detener  
sudo systemctl restart status-monitor    # Reiniciar
sudo systemctl status status-monitor     # Ver estado
```

### **Logs y debugging:**
```bash
sudo journalctl -u status-monitor -f     # Logs en tiempo real
sudo journalctl -u status-monitor --since "1 hour ago"  # Logs última hora
```

### **Actualizar el código:**
```bash
# Detener servicio
sudo systemctl stop status-monitor

# Actualizar código (git pull, editar archivos, etc.)
# ...

# Reinstalar dependencias si cambiaron
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl start status-monitor
```

### **Desinstalar:**
```bash
./desinstalar_servicio.sh
```

## 🔧 **Configuración avanzada**

### **Cambiar puerto (opcional):**
Edita `app.py` y cambia:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### **Configurar firewall:**
```bash
# Permitir puerto 5000
sudo ufw allow 5000

# Ver reglas
sudo ufw status
```

### **Configurar para HTTPS (opcional):**
Para producción, considera usar nginx como proxy reverso con SSL.

## ⚠️ **Solución de problemas**

### **El servicio no inicia:**
```bash
# Ver logs detallados
sudo journalctl -u status-monitor -n 50

# Verificar permisos del archivo .env
ls -la .env
```

### **No se puede acceder desde LAN:**
```bash
# Verificar que el puerto esté abierto
netstat -tlnp | grep :5000

# Verificar firewall
sudo ufw status
```

### **Reinstalar servicio:**
```bash
./desinstalar_servicio.sh
./instalar_servicio.sh
``` 