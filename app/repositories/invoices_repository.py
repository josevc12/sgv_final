from app.db.connection import get_connection


def create_invoice(numero, id_venta, total):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO facturas (numero, id_venta, total) VALUES (?,?,?)",
              (numero, id_venta, total))
    conn.commit()
    conn.close()


def list_invoices(limit=25):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT f.id_factura, f.numero, f.fecha, cl.nombre, f.total, f.estado
        FROM facturas f
        JOIN ventas v  ON v.id_venta   = f.id_venta
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        ORDER BY f.id_factura DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "numero": r[1], "fecha": r[2],
             "cliente": r[3], "total": r[4], "estado": r[5]}
            for r in rows]


def get_invoice_info(id_factura):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT f.id_factura, f.numero, f.fecha, f.total, f.estado,
               v.id_venta, v.subtotal, v.impuestos, v.metodo_pago,
               cl.nombre
        FROM facturas f
        JOIN ventas v  ON v.id_venta = f.id_venta
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        WHERE f.id_factura = ?
    """, (id_factura,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id_factura": row[0],
        "numero": row[1],
        "fecha": row[2],
        "total": row[3],
        "estado": row[4],
        "id_venta": row[5],
        "subtotal": row[6],
        "impuestos": row[7],
        "metodo_pago": row[8],
        "cliente": row[9],
    }


def set_invoice_state(id_factura, state):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE facturas SET estado = ? WHERE id_factura = ?",
              (state, id_factura))
    conn.commit()
    conn.close()
