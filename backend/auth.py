import hashlib
import secrets

# Definición de usuarios con contraseñas hasheadas (SHA-256)
USERS = {
    "ignacio": {
        "username": "Ignacio",
        "role": "Admin",
        "password_hash": hashlib.sha256("Admin123".encode("utf-8")).hexdigest()
    },
    "nacho": {
        "username": "Nacho",
        "role": "User",
        "password_hash": hashlib.sha256("Usuario123".encode("utf-8")).hexdigest()
    }
}

# Almacén de sesiones en memoria: token -> user_info
SESSIONS = {}

def hash_password(password: str) -> str:
    """Hashea una contraseña con SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def authenticate_user(username: str, password: str) -> dict:
    """Valida credenciales y devuelve la info del usuario si son correctas."""
    username_lower = username.lower()
    if username_lower in USERS:
        user = USERS[username_lower]
        if user["password_hash"] == hash_password(password):
            return user
    return None

def create_session(user: dict) -> str:
    """Crea una sesión y devuelve un token seguro."""
    token = secrets.token_hex(32)
    SESSIONS[token] = user
    return token

def get_user_from_token(token: str) -> dict:
    """Obtiene la información del usuario a partir del token de sesión."""
    return SESSIONS.get(token)
