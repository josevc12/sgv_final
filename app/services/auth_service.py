import hashlib

from app.repositories.audit_repository import log_event
from app.repositories.settings_repository import get_setting, set_setting
from app.repositories.users_repository import (
    get_user_by_credentials, update_last_access,
)


def hash_password(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_credentials(username, password):
    user = get_user_by_credentials(username, hash_password(password))
    if user:
        update_last_access(user["id_usuario"])
        log_event("login_exitoso", username, "Sesión iniciada")
        return user
    log_event("login_fallido", username, "Credenciales incorrectas")
    return None


def get_login_preferences():
    remember = get_setting("remember_session", "0") == "1"
    username = get_setting("remembered_username", "") if remember else ""
    return {"remember": remember, "username": username}


def save_login_preferences(username, remember):
    set_setting("remember_session", "1" if remember else "0")
    set_setting("remembered_username", username if remember else "")
