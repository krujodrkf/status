#!/bin/bash

# Script de instalación del servicio Status Monitor para Debian
# Usa 'su' en lugar de 'sudo' para compatibilidad con Debian

echo "🚀 Instalando Status Monitor como servicio del sistema (Debian)..."

# Verificar si tenemos permisos de root o acceso a su
if ! command -v su >/dev/null 2>&1; then
    echo "❌ Error: No se encontró el comando 'su'. ¿Estás en Debian?"
    exit 1
fi

# Función para ejecutar comandos como root
run_as_root() {
    echo "🔐 Ejecutando como root: $*"
    echo "   (Se te pedirá la contraseña de root)"
    su -c "$*"
}

# Verificar si se pasó una ruta como parámetro
if [ -n "$1" ]; then
    PROJECT_DIR="$1"
else
    # Pedir la ruta al usuario
    echo ""
    echo "📁 Por favor, ingresa la ruta completa del proyecto:"
    echo "   Ejemplo: /home/usuario/mi-proyecto/status"
    echo "   O presiona Enter para usar el directorio actual: $(pwd)"
    echo ""
    read -p "Ruta del proyecto: " USER_INPUT
    
    if [ -z "$USER_INPUT" ]; then
        PROJECT_DIR="$(pwd)"
    else
        PROJECT_DIR="$USER_INPUT"
    fi
fi

# Convertir a ruta absoluta
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd 2>/dev/null)"

if [ $? -ne 0 ]; then
    echo "❌ Error: No se puede acceder al directorio: $PROJECT_DIR"
    echo "   Verifica que la ruta existe y tienes permisos."
    exit 1
fi

USER_NAME="$(whoami)"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo "👤 Usuario actual: $USER_NAME"

# Verificar que es un proyecto válido
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "❌ Error: No se encontró app.py en $PROJECT_DIR"
    echo "   ¿Estás seguro de que es la ruta correcta del proyecto?"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "❌ Error: No se encontró requirements.txt en $PROJECT_DIR"
    echo "   ¿Estás seguro de que es la ruta correcta del proyecto?"
    exit 1
fi

echo "✅ Proyecto válido encontrado"

# Verificar que existe el entorno virtual
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ No se encontró el entorno virtual. Creándolo..."
    cd "$PROJECT_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Entorno virtual creado e instalado"
else
    echo "✅ Entorno virtual encontrado"
fi

# Verificar que existe el archivo .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  No se encontró el archivo .env"
    echo "📝 Creando archivo .env de ejemplo..."
    cat > "$PROJECT_DIR/.env" << EOF
# Configuración del servicio Bolivariano
BOLIVARIANO_USERNAME=PBUS@43607
BOLIVARIANO_PASSWORD=dpUhwsa#k@

# Configuración de la aplicación
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo "✅ Archivo .env creado con valores por defecto"
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales:"
    echo "   nano $PROJECT_DIR/.env"
else
    echo "✅ Archivo .env encontrado"
fi

# Verificar dependencias del sistema
echo "📦 Verificando dependencias del sistema..."
if ! run_as_root "apt update"; then
    echo "❌ Error al actualizar repositorios"
    exit 1
fi

# Crear archivo de servicio systemd
echo "📝 Creando archivo de servicio systemd..."
SYSTEMD_SERVICE="/etc/systemd/system/status-monitor.service"

# Crear el contenido del servicio en un archivo temporal
cat > "/tmp/status-monitor.service" << EOF
[Unit]
Description=Status Monitor - Servicio de monitoreo de APIs
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=status-monitor

# Configuración de seguridad
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Copiar el archivo al directorio systemd como root
if ! run_as_root "cp /tmp/status-monitor.service $SYSTEMD_SERVICE"; then
    echo "❌ Error al crear el archivo de servicio"
    exit 1
fi

# Limpiar archivo temporal
rm -f "/tmp/status-monitor.service"

# Recargar systemd
echo "🔄 Recargando systemd..."
if ! run_as_root "systemctl daemon-reload"; then
    echo "❌ Error al recargar systemd"
    exit 1
fi

# Habilitar el servicio para que se inicie al arrancar
echo "🔧 Habilitando servicio para inicio automático..."
if ! run_as_root "systemctl enable status-monitor.service"; then
    echo "❌ Error al habilitar el servicio"
    exit 1
fi

# Iniciar el servicio
echo "▶️  Iniciando servicio..."
if ! run_as_root "systemctl start status-monitor.service"; then
    echo "❌ Error al iniciar el servicio"
    echo "   Verifica los logs con: su -c 'journalctl -u status-monitor -n 20'"
    exit 1
fi

# Esperar un momento para que inicie
sleep 3

# Verificar estado
echo ""
echo "📊 Estado del servicio:"
run_as_root "systemctl status status-monitor.service --no-pager"

# Obtener IP para acceso
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Comandos útiles (como root):"
echo "   Ver estado:     su -c 'systemctl status status-monitor'"
echo "   Detener:        su -c 'systemctl stop status-monitor'"
echo "   Iniciar:        su -c 'systemctl start status-monitor'"
echo "   Reiniciar:      su -c 'systemctl restart status-monitor'"
echo "   Ver logs:       su -c 'journalctl -u status-monitor -f'"
echo "   Deshabilitar:   su -c 'systemctl disable status-monitor'"
echo ""
echo "🌐 Acceso a la aplicación:"
echo "   Local:     http://localhost:5000"
echo "   Desde LAN: http://$IP_ADDRESS:5000"
echo ""
echo "⚠️  Si necesitas editar las credenciales:"
echo "   nano $PROJECT_DIR/.env"
echo "   su -c 'systemctl restart status-monitor'" 