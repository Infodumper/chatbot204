"""
auth.py — Módulo de autenticación y gestión de sesiones.

Implementa un sistema de login basado en SHA-256 con sesiones
en memoria. Los usuarios y contraseñas están definidos de forma
estática (sin base de datos, según restricciones del proyecto).

Limitaciones conocidas:
  - Las sesiones se pierden al reiniciar el servidor.
  - No hay expiración automática de tokens.
"""

import hashlib
import secrets

import os
from dotenv import load_dotenv

load_dotenv()

# Obtener credenciales desde las variables de entorno
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
user_username = os.getenv("USER_USERNAME")
user_password = os.getenv("USER_PASSWORD")

# Validamos que estén configuradas en .env
if not all([admin_username, admin_password, user_username, user_password]):
    raise RuntimeError("Las credenciales de acceso no están configuradas en el archivo .env (ver .env.example)")

# Definición de usuarios con contraseñas hasheadas (SHA-256)
USERS = {
    admin_username.lower(): {
        "username": admin_username,
        "role": "Admin",
        "password_hash": hashlib.sha256(admin_password.encode("utf-8")).hexdigest()
    },
    user_username.lower(): {
        "username": user_username,
        "role": "User",
        "password_hash": hashlib.sha256(user_password.encode("utf-8")).hexdigest()
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
