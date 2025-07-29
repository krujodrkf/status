#!/bin/bash

# Script de instalación del servicio Status Monitor
# Para Ubuntu/Debian

echo "🚀 Instalando Status Monitor como servicio del sistema..."

# Obtener rutas absolutas
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
USER_NAME="$(whoami)"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo "👤 Usuario actual: $USER_NAME"

# Verificar que existe el entorno virtual
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ No se encontró el entorno virtual. Creándolo..."
    python3 -m venv "$PROJECT_DIR/venv"
    source "$PROJECT_DIR/venv/bin/activate"
    pip install -r "$PROJECT_DIR/requirements.txt"
    echo "✅ Entorno virtual creado e instalado"
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
    echo "✅ Archivo .env creado. Por favor edítalo con tus credenciales reales."
fi

# Crear archivo de servicio systemd
echo "📝 Creando archivo de servicio systemd..."
sudo tee /etc/systemd/system/status-monitor.service > /dev/null << EOF
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

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar el servicio para que se inicie al arrancar
echo "🔧 Habilitando servicio para inicio automático..."
sudo systemctl enable status-monitor.service

# Iniciar el servicio
echo "▶️  Iniciando servicio..."
sudo systemctl start status-monitor.service

# Verificar estado
echo ""
echo "📊 Estado del servicio:"
sudo systemctl status status-monitor.service --no-pager

# Obtener IP para acceso
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver estado:     sudo systemctl status status-monitor"
echo "   Detener:        sudo systemctl stop status-monitor"
echo "   Iniciar:        sudo systemctl start status-monitor"
echo "   Reiniciar:      sudo systemctl restart status-monitor"
echo "   Ver logs:       sudo journalctl -u status-monitor -f"
echo "   Deshabilitar:   sudo systemctl disable status-monitor"
echo ""
echo "🌐 Acceso a la aplicación:"
echo "   Local:     http://localhost:5000"
echo "   Desde LAN: http://$IP_ADDRESS:5000"
echo ""
echo "⚠️  Recuerda editar el archivo .env con tus credenciales reales:"
echo "   nano $PROJECT_DIR/.env" 