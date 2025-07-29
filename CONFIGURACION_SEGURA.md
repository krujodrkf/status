# 🔒 Configuración Segura - INSTRUCCIONES IMPORTANTES

## ⚠️ PROBLEMA DE SEGURIDAD SOLUCIONADO

Hemos implementado medidas de seguridad para proteger tus credenciales. **SIGUE ESTOS PASOS OBLIGATORIAMENTE:**

## 📝 Paso 1: Crear archivo .env

Crea un archivo llamado `.env` en la raíz del proyecto con este contenido:

```
# Configuración del servicio Bolivariano
BOLIVARIANO_USERNAME=PBUS@43607
BOLIVARIANO_PASSWORD=dpUhwsa#k@

# Configuración de la aplicación
FLASK_ENV=development
SECRET_KEY=cambia_esta_clave_secreta_por_una_real
```

## 🚀 Paso 2: Reiniciar la aplicación

```bash
# Si la aplicación está corriendo, detenerla con Ctrl+C
# Luego ejecutar de nuevo:
python app.py
```

## ✅ Verificación de Seguridad

Después de aplicar los cambios:

1. **Abre el navegador** en `http://localhost:5000`
2. **Haz click en un segmento verde** para abrir el modal
3. **Verifica que veas:**
   - `userName: [USUARIO_OCULTO]`
   - `password: [PASSWORD_OCULTO]` 
   - `Authorization: Bearer [TOKEN_OCULTO]`

## 🌐 Acceso desde LAN

Para acceder desde otros dispositivos en tu red:

1. **Encuentra tu IP local:**
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig`

2. **Accede desde cualquier dispositivo:**
   - `http://TU_IP_LOCAL:5000`
   - Ejemplo: `http://192.168.4.26:5000`

## 🔐 ¿Qué se ha protegido?

✅ **Credenciales nunca se exponen** en el frontend
✅ **Tokens se ocultan** en las herramientas de desarrollador
✅ **Archivo .env** protegido en `.gitignore`
✅ **Funcionalidad completa** mantenida

## ⚡ Próximos pasos para más servicios

Para agregar más servicios de forma segura:

1. **Agregar credenciales al .env:**
   ```
   NUEVO_SERVICIO_USERNAME=usuario
   NUEVO_SERVICIO_PASSWORD=password
   ```

2. **Actualizar config.py** con la nueva configuración

3. **Crear nuevo servicio** usando el patrón de sanitización 