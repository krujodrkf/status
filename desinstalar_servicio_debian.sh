#!/bin/bash

# Script de desinstalación del servicio Status Monitor para Debian
# Usa 'su' en lugar de 'sudo' para compatibilidad con Debian

echo "🗑️  Desinstalando Status Monitor del sistema (Debian)..."

# Función para ejecutar comandos como root
run_as_root() {
    echo "🔐 Ejecutando como root: $*"
    echo "   (Se te pedirá la contraseña de root)"
    su -c "$*"
}

# Detener el servicio
echo "⏹️  Deteniendo servicio..."
run_as_root "systemctl stop status-monitor.service"

# Deshabilitar el servicio
echo "🔧 Deshabilitando servicio..."
run_as_root "systemctl disable status-monitor.service"

# Eliminar archivo de servicio
echo "🗂️  Eliminando archivo de servicio..."
run_as_root "rm -f /etc/systemd/system/status-monitor.service"

# Recargar systemd
echo "🔄 Recargando systemd..."
run_as_root "systemctl daemon-reload"

# Reset failed units
run_as_root "systemctl reset-failed"

echo ""
echo "✅ Servicio desinstalado correctamente"
echo ""
echo "📝 Nota: Los archivos del proyecto no han sido eliminados."
echo "   Si deseas eliminarlos completamente, hazlo manualmente:"
echo "   rm -rf $(pwd)" 