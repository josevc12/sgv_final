from app.db.connection import get_connection


def get_setting(key, default=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT setting_value FROM app_settings WHERE setting_key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default


def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO app_settings (setting_key, setting_value)
        VALUES (?,?)
        ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value
    """, (key, str(value)))
    conn.commit()
    conn.close()
