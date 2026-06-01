from app.repositories.audit_repository import log_event
from app.repositories.inventory_repository import (
    add_movement, get_inventory_metrics, list_movements,
)
from app.repositories.products_repository import get_product_by_code

VALID_TYPES = {"entrada", "salida", "ajuste"}


def get_metrics():
    return get_inventory_metrics()


def get_recent_movements(limit=25):
    return list_movements(limit)


def register_movement(product_code, mov_type, quantity, reason="", username=""):
    mov_type = mov_type.strip().lower()
    if mov_type not in VALID_TYPES:
        raise ValueError("Tipo inválido: usa entrada, salida o ajuste")

    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        raise ValueError("La cantidad debe ser un número entero")

    if mov_type in {"entrada", "salida"} and qty <= 0:
        raise ValueError("Cantidad debe ser mayor a 0 para entrada o salida")
    if mov_type == "ajuste" and qty == 0:
        raise ValueError("El ajuste no puede ser 0")

    product = get_product_by_code(product_code)
    if not product:
        raise ValueError("Producto no encontrado o inactivo")

    current = int(product["stock"])
    new_stock = current + qty if mov_type in {"entrada", "ajuste"} else current - qty

    if new_stock < 0:
        raise ValueError(f"Stock insuficiente. Disponible: {current}")

    add_movement(
        product_id=product["id"],
        mov_type=mov_type,
        qty=qty,
        stock_before=current,
        stock_after=new_stock,
        reason=reason,
        username=username,
    )
    log_event("inventario", username,
              f"{mov_type} {qty} u. de {product_code.upper()} → stock {new_stock}")
