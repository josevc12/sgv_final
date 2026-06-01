from app.db.connection import get_connection

VALID_TYPES = {"entrada", "salida", "ajuste"}


def add_movement(product_id, mov_type, qty, stock_before, stock_after, reason, username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO movimientos_inventario
        (id_producto, tipo, cantidad, stock_anterior, stock_nuevo, motivo, usuario)
        VALUES (?,?,?,?,?,?,?)
    """, (product_id, mov_type, qty, stock_before, stock_after, reason, username))
    c.execute("UPDATE productos SET stock = ? WHERE id_producto = ?", (stock_after, product_id))
    conn.commit()
    conn.close()


def list_movements(limit=25):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.codigo_producto, p.nombre, m.tipo, m.cantidad,
               m.stock_anterior, m.stock_nuevo, m.fecha, m.usuario, m.motivo
        FROM movimientos_inventario m
        JOIN productos p ON p.id_producto = m.id_producto
        ORDER BY m.id_movimiento DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"codigo": r[0], "nombre": r[1], "tipo": r[2], "cantidad": r[3],
             "stock_anterior": r[4], "stock_nuevo": r[5], "fecha": r[6],
             "usuario": r[7], "motivo": r[8]}
            for r in rows]


def get_inventory_metrics():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM productos WHERE estado = 1")
    total = int(c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM productos WHERE estado = 1 AND stock <= stock_minimo")
    low = int(c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM movimientos_inventario WHERE date(fecha) = date('now')")
    today = int(c.fetchone()[0])
    conn.close()
    return {"total_products": total, "low_stock": low, "movements_today": today}
