import hashlib
from app.db.connection import get_connection


def _ensure_column(cursor, table, column, definition):
    cursor.execute(f"PRAGMA table_info({table})")
    if column not in {row[1] for row in cursor.fetchall()}:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def initialize_database():
    conn = get_connection()
    c = conn.cursor()

    # RF02 – usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT    NOT NULL,
            usuario        TEXT    NOT NULL UNIQUE,
            contrasena     TEXT    NOT NULL,
            rol            TEXT    NOT NULL DEFAULT 'cajero',
            estado         INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT    DEFAULT (datetime('now'))
        )
    """)
    _ensure_column(c, "usuarios", "ultimo_acceso", "TEXT")

    # RF03 – clientes
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT    NOT NULL,
            documento      TEXT    NOT NULL UNIQUE,
            telefono       TEXT    DEFAULT '',
            email          TEXT    DEFAULT '',
            direccion      TEXT    DEFAULT '',
            fecha_registro TEXT    DEFAULT (datetime('now'))
        )
    """)
    # cliente por defecto RF03
    c.execute("INSERT OR IGNORE INTO clientes (nombre, documento) VALUES ('Consumidor Final', 'CF-0000')")

    # RF04 – productos
    c.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto     INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_producto TEXT    NOT NULL UNIQUE,
            nombre          TEXT    NOT NULL,
            descripcion     TEXT    DEFAULT '',
            precio_compra   REAL    NOT NULL DEFAULT 0,
            precio_venta    REAL    NOT NULL DEFAULT 0,
            stock           INTEGER NOT NULL DEFAULT 0,
            stock_minimo    INTEGER NOT NULL DEFAULT 5,
            categoria       TEXT    DEFAULT '',
            estado          INTEGER NOT NULL DEFAULT 1,
            fecha_creacion  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # RF05 – movimientos de inventario
    c.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id_movimiento  INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha          TEXT    DEFAULT (datetime('now')),
            id_producto    INTEGER NOT NULL,
            tipo           TEXT    NOT NULL,
            cantidad       INTEGER NOT NULL,
            stock_anterior INTEGER NOT NULL,
            stock_nuevo    INTEGER NOT NULL,
            motivo         TEXT    DEFAULT '',
            usuario        TEXT    DEFAULT '',
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)

    # RF07 – ventas
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta    INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT    DEFAULT (datetime('now')),
            id_cliente  INTEGER NOT NULL DEFAULT 1,
            id_usuario  INTEGER NOT NULL,
            subtotal    REAL    NOT NULL DEFAULT 0,
            impuestos   REAL    NOT NULL DEFAULT 0,
            total       REAL    NOT NULL DEFAULT 0,
            metodo_pago TEXT    NOT NULL DEFAULT 'efectivo',
            estado      TEXT    NOT NULL DEFAULT 'activa',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    # RF08 – detalle de venta
    c.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id_detalle      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta        INTEGER NOT NULL,
            id_producto     INTEGER NOT NULL,
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL    NOT NULL,
            subtotal        REAL    NOT NULL,
            FOREIGN KEY (id_venta)    REFERENCES ventas(id_venta),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)

    # RF09 – facturas
    c.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
            numero     TEXT    NOT NULL UNIQUE,
            fecha      TEXT    DEFAULT (datetime('now')),
            id_venta   INTEGER NOT NULL UNIQUE,
            total      REAL    NOT NULL DEFAULT 0,
            estado     TEXT    NOT NULL DEFAULT 'activa',
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
        )
    """)

    # RF11/RF12 – caja
    c.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id_caja       INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario    INTEGER NOT NULL,
            fecha_apertura TEXT   DEFAULT (datetime('now')),
            fecha_cierre   TEXT,
            monto_inicial  REAL   NOT NULL DEFAULT 0,
            total_ventas   REAL   DEFAULT 0,
            estado         TEXT   NOT NULL DEFAULT 'abierta',
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    # RF16 – auditoría
    c.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT    DEFAULT (datetime('now')),
            evento    TEXT    NOT NULL,
            usuario   TEXT    DEFAULT '',
            detalle   TEXT    DEFAULT ''
        )
    """)

    # app_settings (sesión recordada)
    c.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key   TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL DEFAULT ''
        )
    """)
    for k, v in [("remember_session", "0"), ("remembered_username", "")]:
        c.execute("INSERT OR IGNORE INTO app_settings VALUES (?,?)", (k, v))

    # usuario admin por defecto
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO usuarios (nombre, usuario, contrasena, rol)
        VALUES ('Administrador', 'admin', ?, 'administrador')
    """, (admin_hash,))

    conn.commit()
    conn.close()
