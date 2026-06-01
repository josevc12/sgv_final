from app.db.connection import get_connection


def get_user_by_credentials(username, password_hash):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_usuario, nombre, usuario, rol
        FROM usuarios
        WHERE usuario = ? AND contrasena = ? AND estado = 1
    """, (username, password_hash))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id_usuario": row[0], "nombre": row[1], "usuario": row[2], "rol": row[3]}


def update_last_access(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE usuarios SET ultimo_acceso = datetime('now') WHERE id_usuario = ?",
                  (user_id,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id_usuario, nombre, usuario, rol, estado FROM usuarios ORDER BY nombre")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "usuario": r[2], "rol": r[3], "estado": r[4]}
            for r in rows]


def create_user(nombre, usuario, password_hash, rol):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (nombre, usuario, contrasena, rol) VALUES (?,?,?,?)",
              (nombre.strip(), usuario.strip(), password_hash, rol))
    conn.commit()
    conn.close()


def set_user_state(user_id, state):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET estado = ? WHERE id_usuario = ?", (state, user_id))
    conn.commit()
    conn.close()


def update_user(user_id, nombre, rol, password_hash=None):
    conn = get_connection()
    c = conn.cursor()
    if password_hash:
        c.execute("""
            UPDATE usuarios
            SET nombre = ?, rol = ?, contrasena = ?
            WHERE id_usuario = ?
        """, (nombre.strip(), rol, password_hash, user_id))
    else:
        c.execute("""
            UPDATE usuarios
            SET nombre = ?, rol = ?
            WHERE id_usuario = ?
        """, (nombre.strip(), rol, user_id))
    conn.commit()
    conn.close()
