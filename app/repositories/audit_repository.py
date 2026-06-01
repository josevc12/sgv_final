from app.db.connection import get_connection


def log_event(event, username="", detail=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO auditoria (evento, usuario, detalle) VALUES (?,?,?)",
                  (event, username, detail))
        conn.commit()
        conn.close()
    except Exception:
        pass


def list_events(limit=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT fecha, evento, usuario, detalle FROM auditoria ORDER BY id_evento DESC LIMIT ?",
              (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"fecha": r[0], "evento": r[1], "usuario": r[2], "detalle": r[3]}
            for r in rows]
