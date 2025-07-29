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

2. Ejecutar la aplicación:
```bash
python app.py
```

3. Abrir navegador en `http://localhost:5000`

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