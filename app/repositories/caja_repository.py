from app.db.connection import get_connection


def get_open_caja(id_usuario):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_caja, monto_inicial, fecha_apertura
        FROM caja
        WHERE id_usuario = ? AND estado = 'abierta'
        ORDER BY id_caja DESC
        LIMIT 1
    """, (id_usuario,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "monto_inicial": row[1], "fecha_apertura": row[2]}
