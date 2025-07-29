# Monitor de Servicios

Sistema de monitoreo simple para verificar el estado de servicios web. Muestra el estado de cada servicio en una barra de tiempo de 24 horas dividida en segmentos de 5 minutos.

## Características

- ✅ Monitoreo automático cada 5 minutos
- 🎯 Barra visual de 24 horas para cada servicio
- 🟢 Verde para servicios funcionando correctamente
- 🔴 Rojo para servicios con errores
- 💬 Tooltip con detalles de request/response al hacer hover
- 📱 Interfaz responsive

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. **CONFIGURACIÓN SEGURA (RECOMENDADO):**
   
   Crea un archivo `.env` en la raíz del proyecto con tus credenciales:
   ```
   # Configuración del servicio Bolivariano
   BOLIVARIANO_USERNAME=tu_usuario_aqui
   BOLIVARIANO_PASSWORD=tu_password_aqui
   
   # Configuración de la aplicación
   FLASK_ENV=development
   SECRET_KEY=cambia_esta_clave_secreta
   ```
   
   **⚠️ IMPORTANTE:** Nunca subas el archivo `.env` a control de versiones.

3. Ejecutar la aplicación:
```bash
python app.py
```

4. Acceder a la aplicación:
   - **Local:** `http://localhost:5000`
   - **Desde LAN:** `http://[IP_DE_TU_MAQUINA]:5000`

## 🚀 Instalación como Servicio del Sistema (Ubuntu)

Para que la aplicación se ejecute automáticamente al iniciar el sistema:

```bash
# Hacer ejecutable el script de instalación
chmod +x instalar_servicio.sh

# Ejecutar instalación
./instalar_servicio.sh
```

### Comandos del Servicio:

```bash
# Ver estado del servicio
sudo systemctl status status-monitor

# Detener servicio
sudo systemctl stop status-monitor

# Iniciar servicio
sudo systemctl start status-monitor

# Reiniciar servicio
sudo systemctl restart status-monitor

# Ver logs en tiempo real
sudo journalctl -u status-monitor -f

# Desinstalar servicio
./desinstalar_servicio.sh
```

## Configuración de Servicios

Los servicios se configuran en el directorio `services/`. Cada servicio debe:

1. Heredar de una clase base o implementar el método `check_service()`
2. Retornar un diccionario con:
   - `status`: 'success' o 'error'
   - `request`: JSON string del request realizado
   - `response`: JSON string de la respuesta recibida
   - `error`: mensaje de error (opcional)

### Ejemplo: Servicio Bolivariano

El servicio Bolivariano está configurado para:
1. Autenticarse obteniendo un token
2. Realizar una consulta de viajes disponibles
3. Verificar que la respuesta tenga la estructura esperada

## Uso

- La página principal muestra todos los servicios configurados
- Cada servicio tiene una barra que representa las 24 horas del día
- Los segmentos cambian de color según el estado:
  - **Gris**: Sin datos
  - **Verde**: Servicio funcionando
  - **Rojo**: Error en el servicio
- Haz hover sobre un segmento rojo para ver detalles del error

## Estructura del Proyecto

```
status/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias
├── services/             
│   ├── __init__.py
│   └── bolivariano.py    # Servicio de ejemplo
├── templates/
│   └── index.html        # Página principal
└── static/
    ├── style.css         # Estilos
    └── script.js         # JavaScript para interactividad
```

## API Endpoints

- `GET /` - Página principal
- `GET /api/data` - Datos de todos los servicios
- `GET /api/data/<servicio>` - Datos de un servicio específico

## 🔒 Seguridad

### Medidas Implementadas:

✅ **Credenciales Protegidas**
- Las credenciales se almacenan en variables de entorno (.env)
- Nunca se exponen en el código fuente

✅ **Sanitización de Datos**
- Los tokens y credenciales se ocultan antes de enviar al frontend
- Usuario/password aparecen como `[USUARIO_OCULTO]` y `[PASSWORD_OCULTO]`
- Tokens aparecen como `Bearer [TOKEN_OCULTO]`

✅ **Frontend Seguro**
- No se pueden ver credenciales reales en herramientas de desarrollador
- Los datos sensibles están protegidos en el servidor

### Acceso desde LAN:

- ✅ **Ya configurado:** La aplicación acepta conexiones desde cualquier IP de la red local
- 🌐 **Acceso:** Usa `http://[IP_DE_TU_MAQUINA]:5000` desde otros dispositivos
- 📱 **Móviles/Tablets:** Funciona perfectamente desde dispositivos móviles en la misma red 