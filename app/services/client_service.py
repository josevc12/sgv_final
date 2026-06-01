import sqlite3

from app.repositories.audit_repository import log_event
from app.repositories.clients_repository import (
    create_client, get_client_purchases, list_clients, update_client,
)


def get_all_clients(search=""):
    return list_clients(search)


def register_client(nombre, documento, telefono="", email="", direccion="", actor=""):
    nombre    = nombre.strip()
    documento = documento.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    if not documento:
        raise ValueError("El documento es obligatorio")
    try:
        create_client(nombre, documento, telefono, email, direccion)
        log_event("cliente_creado", actor, f"Creó cliente '{nombre}' doc={documento}")
    except sqlite3.IntegrityError:
        raise ValueError("El documento ya está registrado")


def get_purchase_history(client_id):
    return get_client_purchases(client_id)


def edit_client(client_id, nombre, documento, telefono="", email="", direccion="", actor=""):
    nombre    = nombre.strip()
    documento = documento.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    if not documento:
        raise ValueError("El documento es obligatorio")
    try:
        update_client(client_id, nombre, documento, telefono, email, direccion)
        log_event("cliente_editado", actor, f"Editó cliente id={client_id}")
    except sqlite3.IntegrityError:
        raise ValueError("El documento ya está registrado")
