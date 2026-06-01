import sqlite3

from app.repositories.audit_repository import log_event
from app.repositories.products_repository import (
    create_product, get_low_stock_products, list_products,
    set_product_state, update_product, get_product_by_code,
)


def get_all_products(search="", only_active=True):
    return list_products(search=search, only_active=only_active)


def get_low_stock():
    return get_low_stock_products()


def find_product_for_sale(query):
    query = query.strip()
    if not query:
        return None, "empty"

    product = get_product_by_code(query)
    if product:
        return product, None

    matches = list_products(search=query, only_active=True)
    if not matches:
        return None, "not_found"
    if len(matches) > 1:
        return None, "multiple"
    return matches[0], None


def register_product(codigo, nombre, precio_compra, precio_venta,
                     stock, stock_minimo, categoria="", descripcion="", actor=""):
    codigo = codigo.strip().upper()
    nombre = nombre.strip()
    if not codigo:
        raise ValueError("El código es obligatorio")
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    try:
        pc = float(precio_compra)
        pv = float(precio_venta)
        st = int(stock)
        sm = int(stock_minimo)
    except (ValueError, TypeError):
        raise ValueError("Precios y stocks deben ser números válidos")
    if pv <= pc:
        raise ValueError("El precio de venta debe ser mayor que el precio de compra")
    if st < 0 or sm < 0:
        raise ValueError("Los valores de stock no pueden ser negativos")
    try:
        create_product(codigo, nombre, descripcion, pc, pv, st, sm, categoria)
        log_event("producto_creado", actor, f"Creó producto {codigo}")
    except sqlite3.IntegrityError:
        raise ValueError("El código de producto ya existe")


def edit_product(product_id, nombre, precio_compra, precio_venta,
                 stock_minimo, categoria, actor=""):
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre es obligatorio")
    try:
        pc = float(precio_compra)
        pv = float(precio_venta)
        sm = int(stock_minimo)
    except (ValueError, TypeError):
        raise ValueError("Precios y stock mínimo deben ser números válidos")
    if pv <= pc:
        raise ValueError("El precio de venta debe ser mayor que el precio de compra")
    update_product(product_id, nombre, pc, pv, sm, categoria)
    log_event("producto_editado", actor, f"Editó producto id={product_id}")


def deactivate_product(product_id, actor=""):
    set_product_state(product_id, 0)
    log_event("producto_desactivado", actor, f"Desactivó producto id={product_id}")


def activate_product(product_id, actor=""):
    set_product_state(product_id, 1)
    log_event("producto_activado", actor, f"Activó producto id={product_id}")
