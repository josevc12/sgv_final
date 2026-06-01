from app.db.connection import get_connection


def list_clients(search=""):
    conn = get_connection()
    c = conn.cursor()
    if search:
        q = f"%{search}%"
        c.execute("""
            SELECT id_cliente, nombre, documento, telefono, email, direccion
            FROM clientes
            WHERE nombre LIKE ? OR documento LIKE ?
            ORDER BY nombre
        """, (q, q))
    else:
        c.execute("""
            SELECT id_cliente, nombre, documento, telefono, email, direccion
            FROM clientes ORDER BY nombre
        """)
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "documento": r[2],
             "telefono": r[3], "email": r[4], "direccion": r[5]}
            for r in rows]


def create_client(nombre, documento, telefono="", email="", direccion=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO clientes (nombre, documento, telefono, email, direccion)
        VALUES (?,?,?,?,?)
    """, (nombre.strip(), documento.strip(), telefono.strip(),
          email.strip(), direccion.strip()))
    conn.commit()
    conn.close()


def update_client(id_cliente, nombre, documento, telefono="", email="", direccion=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE clientes
        SET nombre = ?, documento = ?, telefono = ?, email = ?, direccion = ?
        WHERE id_cliente = ?
    """, (nombre.strip(), documento.strip(), telefono.strip(),
          email.strip(), direccion.strip(), id_cliente))
    conn.commit()
    conn.close()


def get_client_purchases(id_cliente):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT v.id_venta, v.fecha, v.total, v.metodo_pago
        FROM ventas v
        WHERE v.id_cliente = ?
        ORDER BY v.id_venta DESC
        LIMIT 20
    """, (id_cliente,))
    rows = c.fetchall()
    conn.close()
    return rows
