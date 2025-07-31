import requests
import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class AraucaBrasiliaService:
    def __init__(self):
        self.name = "Arauca Brasilia"
        self.base_url = "https://service.expresobrasilia.com/BrasiliaServices"
        
        # Obtener credenciales de forma segura
        service_config = Config.get_service_config('arauca_brasilia')
        self.username = service_config.get('username')
        self.password = service_config.get('password')
        self.token = None
        self.session_id = None
        
    def get_token(self) -> Dict[str, Any]:
        """Obtiene el token de autenticación"""
        url = f"{self.base_url}/login/authenticate"
        
        # Los parámetros van como query parameters
        params = {
            'username': self.username,
            'password': self.password
        }
        
        try:
            response = requests.post(url, params=params, timeout=30)
            request_data = {
                "url": f"{url}?username={self.username}&password={self.password}",
                "method": "POST",
                "headers": {},
                "params": params
            }
            
            if response.status_code == 200:
                # La respuesta puede ser texto plano con el token o JSON
                response_text = response.text.strip()
                
                # Capturar JSESSIONID de las cookies si está disponible
                if 'Set-Cookie' in response.headers:
                    cookies = response.headers.get('Set-Cookie', '')
                    if 'JSESSIONID=' in cookies:
                        # Extraer JSESSIONID
                        import re
                        match = re.search(r'JSESSIONID=([^;]+)', cookies)
                        if match:
                            self.session_id = match.group(1)
                
                # Intentar parsear como JSON primero
                try:
                    data = response.json()
                    # Buscar el token en diferentes lugares posibles de la respuesta
                    token = None
                    if isinstance(data, dict):
                        token = data.get('token') or data.get('access_token') or data.get('accessToken')
                        
                        # Buscar en data si existe
                        if not token and 'data' in data and isinstance(data['data'], dict):
                            token = data['data'].get('token') or data['data'].get('access_token')
                        
                        # Buscar en result si existe  
                        if not token and 'result' in data and isinstance(data['result'], dict):
                            token = data['result'].get('token') or data['result'].get('access_token')
                    
                    if token:
                        self.token = token
                        return {
                            'success': True,
                            'token': self.token,
                            'session_id': self.session_id,
                            'request': request_data,
                            'response': data
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Token not found in JSON response. Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}',
                            'request': request_data,
                            'response': data
                        }
                        
                except json.JSONDecodeError:
                    # Si no es JSON, asumir que la respuesta completa es el token
                    if response_text and len(response_text) > 10:  # Verificar que parece un token
                        self.token = response_text
                        return {
                            'success': True,
                            'token': self.token,
                            'session_id': self.session_id,
                            'request': request_data,
                            'response': response_text
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Invalid token format in plain text response: {response_text}',
                            'request': request_data,
                            'response': response_text
                        }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'request': request_data,
                    'response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'request': {
                    "url": f"{url}?username={self.username}&password={self.password}",
                    "method": "POST",
                    "headers": {},
                    "params": params
                },
                'response': ''
            }
    
    def check_trips_api(self) -> Dict[str, Any]:
        """Verifica la API de viajes disponibles"""
        # Siempre obtener un token nuevo para evitar problemas de vencimiento
        token_result = self.get_token()
        if not token_result['success']:
            return token_result
        
        url = f"{self.base_url}/tickets/getViajes"
        
        # Usar fecha actual en formato DD-MM-AAAA
        current_date = datetime.now().strftime('%d-%m-%Y')
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        # Agregar Cookie JSESSIONID si está disponible
        if self.session_id:
            headers['Cookie'] = f'JSESSIONID={self.session_id}'
        
        # Los parámetros van como query parameters
        params = {
            'codOrigen': 'BOG',
            'codDestino': 'MDE', 
            'fechaViaje': current_date
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, timeout=30)
            
            request_data = {
                "url": f"{url}?codOrigen=BOG&codDestino=MDE&fechaViaje={current_date}",
                "method": "POST",
                "headers": headers,
                "params": params
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura esperada según los requerimientos
                # La respuesta debe ser un array con objetos que contengan los campos requeridos
                if isinstance(data, list) and len(data) > 0:
                    # Verificar que al menos el primer elemento tenga los campos requeridos
                    first_item = data[0]
                    required_fields = ['codigoOrigen', 'nombreOrigen', 'codigoDestino', 'nombreDestino', 'fechaViaje', 'lineas', 'isConexion']
                    
                    if all(field in first_item for field in required_fields):
                        return {
                            'success': True,
                            'request': request_data,
                            'response': data
                        }
                    else:
                        missing_fields = [field for field in required_fields if field not in first_item]
                        return {
                            'success': False,
                            'error': f'Missing required fields in response: {missing_fields}. Available fields: {list(first_item.keys())}',
                            'request': request_data,
                            'response': data
                        }
                elif isinstance(data, list) and len(data) == 0:
                    # Lista vacía puede ser válida (sin viajes disponibles)
                    return {
                        'success': True,
                        'request': request_data,
                        'response': data
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Invalid response structure. Expected array, got: {type(data)}',
                        'request': request_data,
                        'response': data
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'request': request_data,
                    'response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'request': {
                    "url": f"{url}?codOrigen=BOG&codDestino=MDE&fechaViaje={current_date}",
                    "method": "POST",
                    "headers": headers,
                    "params": params
                },
                'response': ''
            }
    
    def sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina datos sensibles del request antes de enviarlo al frontend"""
        sanitized = request_data.copy()
        
        # Eliminar credenciales de headers
        if 'headers' in sanitized:
            headers = sanitized['headers'].copy()
            if 'Authorization' in headers:
                headers['Authorization'] = 'Bearer [TOKEN_OCULTO]'
            if 'Cookie' in headers:
                headers['Cookie'] = 'JSESSIONID=[SESSION_OCULTA]'
            sanitized['headers'] = headers
        
        # Eliminar credenciales de los parámetros de la URL
        if 'url' in sanitized:
            url = sanitized['url']
            if 'username=' in url and 'password=' in url:
                # Reemplazar credenciales en la URL
                import re
                url = re.sub(r'username=[^&]+', 'username=[USUARIO_OCULTO]', url)
                url = re.sub(r'password=[^&]+', 'password=[PASSWORD_OCULTO]', url)
                sanitized['url'] = url
        
        # Eliminar credenciales de params si existen
        if 'params' in sanitized and isinstance(sanitized['params'], dict):
            params = sanitized['params'].copy()
            if 'username' in params:
                params['username'] = '[USUARIO_OCULTO]'
            if 'password' in params:
                params['password'] = '[PASSWORD_OCULTO]'
            sanitized['params'] = params
        
        return sanitized
    
    def check_service(self) -> Dict[str, Any]:
        """Verificación principal del servicio"""
        result = self.check_trips_api()
        
        if result['success']:
            # Sanitizar datos antes de enviar al frontend
            sanitized_request = self.sanitize_request_data(result['request'])
            
            return {
                'status': 'success',
                'request': json.dumps(sanitized_request, indent=2),
                'response': json.dumps(result['response'], indent=2)
            }
        else:
            # Sanitizar datos antes de enviar al frontend
            sanitized_request = self.sanitize_request_data(result['request']) if 'request' in result else {}
            
            return {
                'status': 'error',
                'request': json.dumps(sanitized_request, indent=2) if sanitized_request else '',
                'response': json.dumps(result['response'], indent=2) if 'response' in result else '',
                'error': result['error']
            }