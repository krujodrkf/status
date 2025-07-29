#!/usr/bin/env python3
"""
Script de prueba para el monitor de servicios.
Permite probar el funcionamiento sin hacer requests reales a los servicios.
"""

import time
import requests
import json
from datetime import datetime

def test_api():
    """Prueba los endpoints de la API"""
    base_url = "http://localhost:5000"
    
    print("🔄 Probando el monitor de servicios...")
    print(f"📍 URL base: {base_url}")
    
    try:
        # Probar página principal
        print("\n1. Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal OK")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
            return
        
        # Esperar un poco para que se ejecute el primer check
        print("\n2. Esperando primera verificación de servicios...")
        time.sleep(10)
        
        # Probar API de datos
        print("\n3. Probando API de datos...")
        response = requests.get(f"{base_url}/api/data")
        if response.status_code == 200:
            data = response.json()
            print("✅ API de datos OK")
            print(f"📊 Servicios encontrados: {list(data.keys())}")
            
            # Mostrar datos del servicio bolivariano si existen
            if 'bolivariano' in data:
                bolivariano_data = data['bolivariano']
                print(f"📈 Bolivariano tiene {len(bolivariano_data)} registros")
                
                # Mostrar último registro
                if bolivariano_data:
                    times = sorted(bolivariano_data.keys())
                    last_time = times[-1]
                    last_record = bolivariano_data[last_time]
                    print(f"🕐 Último registro: {last_time}")
                    print(f"📊 Estado: {last_record['status']}")
                    if last_record['status'] == 'error':
                        print(f"❌ Error: {last_record.get('error', 'No especificado')}")
        else:
            print(f"❌ Error en API de datos: {response.status_code}")
            return
        
        # Probar API específica del servicio
        print("\n4. Probando API del servicio Bolivariano...")
        response = requests.get(f"{base_url}/api/data/bolivariano")
        if response.status_code == 200:
            print("✅ API del servicio Bolivariano OK")
        else:
            print(f"❌ Error en API del servicio: {response.status_code}")
        
        print(f"\n🎉 ¡Pruebas completadas! Visita {base_url} en tu navegador.")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose la aplicación?")
        print("💡 Ejecuta: python app.py")
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")

if __name__ == "__main__":
    test_api() 