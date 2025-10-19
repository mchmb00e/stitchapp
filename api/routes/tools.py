# ==============================================================================
# Módulo de Herramientas (tools.py)
# ------------------------------------------------------------------------------
# Este archivo contiene funciones de utilidad reutilizables en toda la
# aplicación, como la estandarización de respuestas de la API y la generación
# de tokens seguros.
# ==============================================================================

import secrets
import string

def schema(status: int, description: str, res):
    """
    Estandariza el formato de las respuestas de la API.
    
    Crea un diccionario con una estructura consistente para todas las respuestas
    del servidor, facilitando el procesamiento en el lado del cliente.
    
    Args:
        status (int): El código de estado HTTP (ej: 200, 404, 500).
        description (str): Una descripción legible para el humano sobre el resultado.
        res: El cuerpo de la respuesta o los datos a devolver. Puede ser un
             diccionario, una lista, etc.
             
    Returns:
        dict: Un diccionario con la estructura de respuesta estándar.
    """
    return {
        'estado': status,
        'descripcion': description,
        'res': res
    }

def generate_token(length=255):
    """
    Genera un token alfanumérico criptográficamente seguro.
    
    Utiliza el módulo 'secrets' de Python para garantizar que el token sea
    adecuado para usos de seguridad, como la identificación de medios.
    
    Args:
        length (int, optional): La longitud deseada para el token.
                                 Por defecto es 255.
                                 
    Returns:
        str: El token seguro generado.
    """
    # Define el alfabeto de caracteres a utilizar para el token.
    chars = string.ascii_letters + string.digits
    # Genera y une caracteres aleatorios seguros del alfabeto.
    return ''.join(secrets.choice(chars) for _ in range(length))
