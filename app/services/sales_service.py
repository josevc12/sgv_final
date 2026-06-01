from datetime import datetime

from app.db.connection import get_connection
from app.repositories.audit_repository import log_event
from app.repositories.invoices_repository import create_invoice
from app.repositories.sales_repository import (
    add_sale_detail, create_sale, get_sale_items, list_sales,
)

TAX_RATE = 0.19  # IVA 19%


def get_all_sales(limit=25):
    return list_sales(limit)


def get_items_for_sale(sale_id):
    return get_sale_items(sale_id)


def confirm_sale(id_usuario, id_cliente, items, metodo_pago, username):
    """
    items: [{"id_producto": int, "nombre": str, "cantidad": int, "precio_unitario": float}]
    Ejecuta todo en una única transacción:
      1. Crea la venta
      2. Inserta el detalle
      3. Descuenta el stock con movimiento de inventario
      4. Genera la factura
    """
    if not items:
        raise ValueError("El carrito está vacío")

    metodo_pago = metodo_pago.strip().lower()
    if metodo_pago not in {"efectivo", "tarjeta", "transferencia", "mixto"}:
        raise ValueError("Método de pago inválido")

    subtotal  = round(sum(i["cantidad"] * i["precio_unitario"] for i in items), 2)
    impuestos = round(subtotal * TAX_RATE, 2)
    total     = round(subtotal + impuestos, 2)

    conn = get_connection()
    c = conn.cursor()
    try:
        # 1. Venta
        c.execute("""
            INSERT INTO ventas (id_cliente, id_usuario, subtotal, impuestos, total, metodo_pago)
            VALUES (?,?,?,?,?,?)
        """, (id_cliente, id_usuario, subtotal, impuestos, total, metodo_pago))
        id_venta = c.lastrowid

        for item in items:
            sub_item = round(item["cantidad"] * item["precio_unitario"], 2)

            # 2. Detalle
            c.execute("""
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?,?,?,?,?)
            """, (id_venta, item["id_producto"], item["cantidad"],
                  item["precio_unitario"], sub_item))

            # 3. Stock
            c.execute("SELECT stock FROM productos WHERE id_producto = ?", (item["id_producto"],))
            current = int(c.fetchone()[0])
            new_stock = current - item["cantidad"]
            if new_stock < 0:
                raise ValueError(f"Stock insuficiente para '{item['nombre']}'")

            c.execute("UPDATE productos SET stock = ? WHERE id_producto = ?",
                      (new_stock, item["id_producto"]))
            c.execute("""
                INSERT INTO movimientos_inventario
                (id_producto, tipo, cantidad, stock_anterior, stock_nuevo, motivo, usuario)
                VALUES (?,?,?,?,?,?,?)
            """, (item["id_producto"], "salida", item["cantidad"],
                  current, new_stock, f"venta #{id_venta}", username))

        # 4. Factura
        numero = f"FAC-{datetime.now().strftime('%Y%m%d')}-{id_venta:04d}"
        c.execute("INSERT INTO facturas (numero, id_venta, total) VALUES (?,?,?)",
                  (numero, id_venta, total))

        conn.commit()
        log_event("venta_realizada", username,
                  f"Venta #{id_venta} | {numero} | ${total:.2f} | {metodo_pago}")
        return {"id_venta": id_venta, "numero_factura": numero,
                "subtotal": subtotal, "impuestos": impuestos, "total": total}

    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        conn.close()
