from app.db.connection import get_connection


def create_sale(id_cliente, id_usuario, subtotal, impuestos, total, metodo_pago):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ventas (id_cliente, id_usuario, subtotal, impuestos, total, metodo_pago)
        VALUES (?,?,?,?,?,?)
    """, (id_cliente, id_usuario, subtotal, impuestos, total, metodo_pago))
    sale_id = c.lastrowid
    conn.commit()
    conn.close()
    return sale_id


def add_sale_detail(id_venta, id_producto, cantidad, precio_unitario, subtotal):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
        VALUES (?,?,?,?,?)
    """, (id_venta, id_producto, cantidad, precio_unitario, subtotal))
    conn.commit()
    conn.close()


def list_sales(limit=25):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT v.id_venta, v.fecha, cl.nombre, u.nombre,
               v.subtotal, v.impuestos, v.total, v.metodo_pago, v.estado,
               COALESCE(f.numero, '')
        FROM ventas v
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        JOIN usuarios u  ON u.id_usuario  = v.id_usuario
        LEFT JOIN facturas f ON f.id_venta = v.id_venta
        ORDER BY v.id_venta DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "fecha": r[1], "cliente": r[2], "cajero": r[3],
             "subtotal": r[4], "impuestos": r[5], "total": r[6],
             "metodo": r[7], "estado": r[8], "factura": r[9]}
            for r in rows]


def get_sale_items(id_venta):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal
        FROM detalle_venta dv
        JOIN productos p ON p.id_producto = dv.id_producto
        WHERE dv.id_venta = ?
    """, (id_venta,))
    rows = c.fetchall()
    conn.close()
    return [{"nombre": r[0], "cantidad": r[1], "precio": r[2], "subtotal": r[3]}
            for r in rows]


def set_sale_state(id_venta, state):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE ventas SET estado = ? WHERE id_venta = ?", (state, id_venta))
    conn.commit()
    conn.close()
