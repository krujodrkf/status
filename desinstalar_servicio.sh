#!/bin/bash

# Script de desinstalación del servicio Status Monitor

echo "🗑️  Desinstalando Status Monitor del sistema..."

# Detener el servicio
echo "⏹️  Deteniendo servicio..."
sudo systemctl stop status-monitor.service

# Deshabilitar el servicio
echo "🔧 Deshabilitando servicio..."
sudo systemctl disable status-monitor.service

# Eliminar archivo de servicio
echo "🗂️  Eliminando archivo de servicio..."
sudo rm -f /etc/systemd/system/status-monitor.service

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Reset failed units
sudo systemctl reset-failed

echo ""
echo "✅ Servicio desinstalado correctamente"
echo ""
echo "📝 Nota: Los archivos del proyecto no han sido eliminados."
echo "   Si deseas eliminarlos completamente, hazlo manualmente:"
echo "   rm -rf $(pwd)" 