import requests
import json
from datetime import datetime
from typing import Dict, Any

class BolivarianoService:
    def __init__(self):
        self.name = "Bolivariano"
        self.base_url = "https://apis.bolivariano.com.co"
        self.username = "PBUS@43607"
        self.password = "dpUhwsa#k@"
        self.token = None
        
    def get_token(self) -> Dict[str, Any]:
        """Obtiene el token de autenticación"""
        url = f"{self.base_url}/authentication/v1/Authentication/UserLogin"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "userName": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            request_data = {
                "url": url,
                "method": "POST",
                "headers": headers,
                "body": payload
            }
            
            if response.status_code == 200:
                data = response.json()
                # Buscar el token en diferentes lugares posibles de la respuesta
                token = None
                if isinstance(data, dict):
                    # Buscar directamente en la raíz
                    token = data.get('token') or data.get('access_token') or data.get('accessToken')
                    
                    # Buscar en data si existe
                    if not token and 'data' in data and isinstance(data['data'], dict):
                        token = data['data'].get('token') or data['data'].get('access_token') or data['data'].get('accessToken')
                    
                    # Buscar en result si existe
                    if not token and 'result' in data and isinstance(data['result'], dict):
                        token = data['result'].get('token') or data['result'].get('access_token') or data['result'].get('accessToken')
                
                if token:
                    self.token = token
                    return {
                        'success': True,
                        'token': self.token,
                        'request': request_data,
                        'response': data
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Token not found in response. Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}',
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
                    "url": url,
                    "method": "POST",
                    "headers": headers,
                    "body": payload
                },
                'response': ''
            }
    
    def check_trips_api(self) -> Dict[str, Any]:
        """Verifica la API de viajes disponibles"""
        if not self.token:
            token_result = self.get_token()
            if not token_result['success']:
                return token_result
        
        url = f"{self.base_url}/weballiates/V1/Sales/GetAvailableTripsRoundTrip"
        
        # Usar fecha actual
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Client-Header-Info': '{"ClientIP":"54.203.172.96", "ClientInfo":"pinbus"}'
        }
        
        payload = {
            "originAgencyId": "1",
            "destinationAgencyId": "5",
            "outboundTripDate": f"{current_date}T00:00:00Z",
            "outboundTotalPassengers": 1,
            "outboundTimeOfDay": 0,
            "returnTripDate": None,
            "returnTotalPassengers": 0,
            "returnTimeOfDay": 0
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            request_data = {
                "url": url,
                "method": "POST",
                "headers": headers,
                "body": payload
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura esperada
                if (isinstance(data, dict) and 
                    'statusCode' in data and 
                    'data' in data and 
                    isinstance(data['data'], dict) and
                    'outboundTrips' in data['data']):
                    
                    return {
                        'success': True,
                        'request': request_data,
                        'response': data
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Invalid response structure',
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
                    "url": url,
                    "method": "POST",
                    "headers": headers,
                    "body": payload
                },
                'response': ''
            }
    
    def check_service(self) -> Dict[str, Any]:
        """Verificación principal del servicio"""
        result = self.check_trips_api()
        
        if result['success']:
            return {
                'status': 'success',
                'request': json.dumps(result['request'], indent=2),
                'response': json.dumps(result['response'], indent=2)
            }
        else:
            return {
                'status': 'error',
                'request': json.dumps(result['request'], indent=2) if 'request' in result else '',
                'response': json.dumps(result['response'], indent=2) if 'response' in result else '',
                'error': result['error']
            } 