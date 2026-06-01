from app.repositories.audit_repository import log_event
from app.repositories.users_repository import (
    create_user, list_users, set_user_state, update_user,
)
from app.services.auth_service import hash_password

VALID_ROLES = {"administrador", "cajero", "supervisor"}


def get_all_users():
    return list_users()


def register_user(nombre, usuario, password, rol, actor=""):
    nombre  = nombre.strip()
    usuario = usuario.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    if not usuario:
        raise ValueError("El usuario es obligatorio")
    if len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres")
    if rol not in VALID_ROLES:
        raise ValueError(f"Rol inválido. Opciones: {', '.join(VALID_ROLES)}")
    create_user(nombre, usuario, hash_password(password), rol)
    log_event("usuario_creado", actor, f"Creó usuario '{usuario}' rol '{rol}'")


def toggle_user(user_id, current_state, actor=""):
    new_state = 0 if current_state == 1 else 1
    set_user_state(user_id, new_state)
    action = "desactivó" if new_state == 0 else "activó"
    log_event("usuario_modificado", actor, f"{action} usuario id={user_id}")


def edit_user(user_id, nombre, rol, password="", actor=""):
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    if rol not in VALID_ROLES:
        raise ValueError(f"Rol inválido. Opciones: {', '.join(VALID_ROLES)}")
    pwd_hash = None
    if password:
        if len(password) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres")
        pwd_hash = hash_password(password)
    update_user(user_id, nombre, rol, pwd_hash)
    log_event("usuario_editado", actor, f"Editó usuario id={user_id}")
