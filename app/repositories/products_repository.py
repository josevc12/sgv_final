from app.db.connection import get_connection


def list_products(search="", only_active=True):
    conn = get_connection()
    c = conn.cursor()
    where, params = [], []
    if only_active:
        where.append("estado = 1")
    if search:
        where.append("(nombre LIKE ? OR codigo_producto LIKE ?)")
        q = f"%{search}%"
        params += [q, q]
    sql = ("SELECT id_producto, codigo_producto, nombre, precio_compra, precio_venta, "
           "stock, stock_minimo, categoria, estado, descripcion FROM productos")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY nombre"
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "codigo": r[1], "nombre": r[2], "precio_compra": r[3],
             "precio_venta": r[4], "stock": r[5], "stock_minimo": r[6],
             "categoria": r[7], "estado": r[8], "descripcion": r[9]}
            for r in rows]


def get_product_by_code(code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_producto, codigo_producto, nombre, precio_compra, precio_venta,
               stock, stock_minimo, categoria, descripcion
        FROM productos
        WHERE codigo_producto = ? AND estado = 1
    """, (code.upper().strip(),))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "codigo": row[1], "nombre": row[2], "precio_compra": row[3],
            "precio_venta": row[4], "stock": row[5], "stock_minimo": row[6],
            "categoria": row[7], "descripcion": row[8]}


def create_product(codigo, nombre, descripcion, precio_compra, precio_venta,
                   stock, stock_minimo, categoria):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO productos
        (codigo_producto, nombre, descripcion, precio_compra, precio_venta,
         stock, stock_minimo, categoria)
        VALUES (?,?,?,?,?,?,?,?)
    """, (codigo.upper().strip(), nombre.strip(), descripcion.strip(),
          float(precio_compra), float(precio_venta),
          int(stock), int(stock_minimo), categoria.strip()))
    conn.commit()
    conn.close()


def update_product(product_id, nombre, precio_compra, precio_venta, stock_minimo, categoria):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE productos
        SET nombre = ?, precio_compra = ?, precio_venta = ?,
            stock_minimo = ?, categoria = ?
        WHERE id_producto = ?
    """, (nombre.strip(), float(precio_compra), float(precio_venta),
          int(stock_minimo), categoria.strip(), product_id))
    conn.commit()
    conn.close()


def set_product_state(product_id, state):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE productos SET estado = ? WHERE id_producto = ?", (state, product_id))
    conn.commit()
    conn.close()


def get_low_stock_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_producto, codigo_producto, nombre, stock, stock_minimo
        FROM productos
        WHERE estado = 1 AND stock <= stock_minimo
        ORDER BY stock ASC
    """)
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "codigo": r[1], "nombre": r[2],
             "stock": r[3], "stock_minimo": r[4]} for r in rows]
