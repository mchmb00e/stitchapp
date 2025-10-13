import secrets
import string

def schema(status: int, description: str, res):
    return {
        'estado': status,
        'descripcion': description,
        'res': res
    }
def generate_token(length=255):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))