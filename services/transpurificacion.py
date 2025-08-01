import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class TranspurificacionService:
    def __init__(self):
        self.name = "Transpurificación"
        self.base_url = "http://puri.fsl.sisorgcloud.com/PINBUS"
        
        # Obtener credenciales de forma segura
        service_config = Config.get_service_config('transpurificacion')
        self.key = service_config.get('key')
        self.consumer_id = service_config.get('consumer_id')
        self.token = None
        
    def get_token(self) -> Dict[str, Any]:
        """Obtiene el token de autenticación usando SOAP"""
        url = f"{self.base_url}/token.asmx"
        
        headers = {
            'Content-Type': 'application/soap+xml'
        }
        
        # SOAP XML para obtener token
        soap_body = f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:agil="http://agilis.fics.fsl.sisorg.com.ar/">
   <soap:Header/>
   <soap:Body>
      <agil:GetToken>
         <agil:Key>{self.key}</agil:Key>
         <agil:ConsumerID>{self.consumer_id}</agil:ConsumerID>
      </agil:GetToken>
   </soap:Body>
</soap:Envelope>'''
        
        try:
            response = requests.post(url, headers=headers, data=soap_body, timeout=30)
            request_data = {
                "url": url,
                "method": "POST",
                "headers": headers,
                "body": soap_body
            }
            
            if response.status_code == 200:
                try:
                    # Parsear respuesta XML SOAP
                    root = ET.fromstring(response.text)
                    
                    # Buscar el token en la respuesta
                    # Namespaces para SOAP
                    namespaces = {
                        'soap': 'http://www.w3.org/2003/05/soap-envelope',
                        'agil': 'http://agilis.fics.fsl.sisorg.com.ar/'
                    }
                    
                    # Buscar GetTokenResult
                    token_result = root.find('.//agil:GetTokenResult', namespaces)
                    if token_result is not None and token_result.text:
                        token_xml = token_result.text.strip()
                        
                        # El token viene como XML anidado, necesito extraer el valor del atributo Token
                        try:
                            token_root = ET.fromstring(token_xml)
                            token_value = token_root.get('Token')
                            if token_value:
                                self.token = token_value
                                return {
                                    'success': True,
                                    'token': self.token,
                                    'request': request_data,
                                    'response': response.text
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': 'Token attribute not found in XML token response',
                                    'request': request_data,
                                    'response': response.text
                                }
                        except ET.ParseError as e:
                            return {
                                'success': False,
                                'error': f'Error parsing token XML: {str(e)}',
                                'request': request_data,
                                'response': response.text
                            }
                    else:
                        return {
                            'success': False,
                            'error': 'Token not found in SOAP response',
                            'request': request_data,
                            'response': response.text
                        }
                        
                except ET.ParseError as e:
                    return {
                        'success': False,
                        'error': f'Error parsing SOAP XML: {str(e)}',
                        'request': request_data,
                        'response': response.text
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
                    "body": soap_body
                },
                'response': ''
            }
    
    def check_trips_api(self) -> Dict[str, Any]:
        """Verifica la API de viajes disponibles usando SOAP"""
        # Siempre obtener un token nuevo para evitar problemas de vencimiento
        token_result = self.get_token()
        if not token_result['success']:
            return token_result
        
        url = f"{self.base_url}/viaje.asmx"
        
        # Usar fecha actual en formato DD/MM/AAAA 00:00:00
        current_date = datetime.now().strftime('%d/%m/%Y 00:00:00')
        
        headers = {
            'Content-Type': 'application/soap+xml'
        }
        
        # SOAP XML para obtener viajes disponibles
        soap_body = f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:agil="http://agilis.fics.fsl.sisorg.com.ar/">
   <soap:Header/>
   <soap:Body>
      <agil:GetDisponiblesIda>
         <agil:Token>{self.token}</agil:Token>
         <agil:Fecha>{current_date}</agil:Fecha>
         <agil:TerminalOrigenID>1</agil:TerminalOrigenID>
         <agil:TerminalDestinoID>7</agil:TerminalDestinoID>
         <agil:FechaAbierta>0</agil:FechaAbierta>
         <agil:BuscarTodosLosHorarios>1</agil:BuscarTodosLosHorarios>
         <agil:PuestoTrabajoID>1</agil:PuestoTrabajoID>
         <agil:Operacion>1</agil:Operacion>
         <agil:ModoResultados>0</agil:ModoResultados>
         <agil:CantidadPasajeros>0</agil:CantidadPasajeros>
      </agil:GetDisponiblesIda>
   </soap:Body>
</soap:Envelope>'''
        
        try:
            response = requests.post(url, headers=headers, data=soap_body, timeout=30)
            
            request_data = {
                "url": url,
                "method": "POST",
                "headers": headers,
                "body": soap_body
            }
            
            if response.status_code == 200:
                try:
                    # Parsear respuesta XML SOAP
                    root = ET.fromstring(response.text)
                    
                    # Namespaces para SOAP
                    namespaces = {
                        'soap': 'http://www.w3.org/2003/05/soap-envelope',
                        'agil': 'http://agilis.fics.fsl.sisorg.com.ar/'
                    }
                    
                    # Buscar GetDisponiblesIdaResult
                    result_element = root.find('.//agil:GetDisponiblesIdaResult', namespaces)
                    if result_element is not None and result_element.text:
                        # El contenido está como XML anidado en texto
                        inner_xml = result_element.text
                        
                        try:
                            # Parsear el XML interno
                            inner_root = ET.fromstring(inner_xml)
                            
                            # Buscar elementos viaje
                            viajes = inner_root.findall('.//viaje')
                            
                            if viajes:
                                # Verificar que al menos haya elementos viaje con atributos básicos
                                first_viaje = viajes[0]
                                required_attrs = ['TerminalOrigenNombre', 'TerminalDestinoNombre', 'FechaPartida', 'ButacasDisponibles']
                                
                                if all(attr in first_viaje.attrib for attr in required_attrs):
                                    return {
                                        'success': True,
                                        'request': request_data,
                                        'response': {
                                            'xml_response': response.text,
                                            'parsed_data': {
                                                'total_viajes': len(viajes),
                                                'fecha_consulta': current_date,
                                                'primer_viaje': dict(first_viaje.attrib)
                                            }
                                        }
                                    }
                                else:
                                    missing_attrs = [attr for attr in required_attrs if attr not in first_viaje.attrib]
                                    return {
                                        'success': False,
                                        'error': f'Missing required attributes in viaje: {missing_attrs}. Available: {list(first_viaje.attrib.keys())}',
                                        'request': request_data,
                                        'response': response.text
                                    }
                            else:
                                # No hay viajes disponibles pero la estructura es válida
                                return {
                                    'success': True,
                                    'request': request_data,
                                    'response': {
                                        'xml_response': response.text,
                                        'parsed_data': {
                                            'total_viajes': 0,
                                            'fecha_consulta': current_date,
                                            'mensaje': 'No hay viajes disponibles para la fecha consultada'
                                        }
                                    }
                                }
                                
                        except ET.ParseError as e:
                            return {
                                'success': False,
                                'error': f'Error parsing inner XML: {str(e)}',
                                'request': request_data,
                                'response': response.text
                            }
                    else:
                        return {
                            'success': False,
                            'error': 'GetDisponiblesIdaResult not found in SOAP response',
                            'request': request_data,
                            'response': response.text
                        }
                        
                except ET.ParseError as e:
                    return {
                        'success': False,
                        'error': f'Error parsing SOAP XML: {str(e)}',
                        'request': request_data,
                        'response': response.text
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
                    "body": soap_body
                },
                'response': ''
            }
    
    def sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina datos sensibles del request antes de enviarlo al frontend"""
        sanitized = request_data.copy()
        
        # Sanitizar el SOAP XML body
        if 'body' in sanitized and isinstance(sanitized['body'], str):
            body = sanitized['body']
            # Reemplazar credenciales en el XML
            if self.key in body:
                body = body.replace(self.key, '[KEY_OCULTA]')
            if self.consumer_id in body:
                body = body.replace(self.consumer_id, '[CONSUMER_ID_OCULTO]')
            if self.token and self.token in body:
                body = body.replace(self.token, '[TOKEN_OCULTO]')
            sanitized['body'] = body
        
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