import flet as ft

from app.db.connection import get_connection
from app.repositories.products_repository import get_low_stock_products
from app.views.shared import (
    C, card, field, pall, psym, primary_btn, render_page,
    section_title, show_snack, status_chip,
)


# ── queries de reportes ───────────────────────────────────────────────────────

def _ventas_diarias(fecha=None):
    """Ventas de un día específico. Sin fecha = hoy."""
    conn = get_connection()
    c = conn.cursor()
    filtro = fecha if fecha else "date('now')"
    c.execute(f"""
        SELECT v.id_venta, v.fecha, cl.nombre, u.nombre,
               v.total, v.metodo_pago, COALESCE(f.numero,'')
        FROM ventas v
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        JOIN usuarios u  ON u.id_usuario  = v.id_usuario
        LEFT JOIN facturas f ON f.id_venta = v.id_venta
        WHERE date(v.fecha) = ? AND v.estado = 'activa'
        ORDER BY v.id_venta DESC
    """, (filtro if fecha else "date('now')",))
    if fecha:
        pass
    else:
        c.execute("""
            SELECT v.id_venta, v.fecha, cl.nombre, u.nombre,
                   v.total, v.metodo_pago, COALESCE(f.numero,'')
            FROM ventas v
            JOIN clientes cl ON cl.id_cliente = v.id_cliente
            JOIN usuarios u  ON u.id_usuario  = v.id_usuario
            LEFT JOIN facturas f ON f.id_venta = v.id_venta
            WHERE date(v.fecha) = date('now') AND v.estado = 'activa'
            ORDER BY v.id_venta DESC
        """)
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "fecha": r[1], "cliente": r[2], "cajero": r[3],
             "total": r[4], "metodo": r[5], "factura": r[6]} for r in rows]


def _ventas_por_periodo(desde, hasta):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT v.id_venta, v.fecha, cl.nombre, u.nombre,
               v.total, v.metodo_pago, COALESCE(f.numero,'')
        FROM ventas v
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        JOIN usuarios u  ON u.id_usuario  = v.id_usuario
        LEFT JOIN facturas f ON f.id_venta = v.id_venta
        WHERE date(v.fecha) BETWEEN ? AND ? AND v.estado = 'activa'
        ORDER BY v.id_venta DESC
    """, (desde, hasta))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "fecha": r[1], "cliente": r[2], "cajero": r[3],
             "total": r[4], "metodo": r[5], "factura": r[6]} for r in rows]


def _productos_mas_vendidos(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.codigo_producto, p.nombre, SUM(dv.cantidad) as unidades,
               SUM(dv.subtotal) as ingresos
        FROM detalle_venta dv
        JOIN productos p ON p.id_producto = dv.id_producto
        JOIN ventas v ON v.id_venta = dv.id_venta
        WHERE v.estado = 'activa'
        GROUP BY dv.id_producto
        ORDER BY unidades DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"codigo": r[0], "nombre": r[1], "unidades": r[2], "ingresos": r[3]}
            for r in rows]


def _clientes_top(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT cl.nombre, cl.documento,
               COUNT(v.id_venta) as num_compras,
               SUM(v.total) as total_comprado
        FROM ventas v
        JOIN clientes cl ON cl.id_cliente = v.id_cliente
        WHERE v.estado = 'activa'
        GROUP BY v.id_cliente
        ORDER BY total_comprado DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"nombre": r[0], "documento": r[1],
             "compras": r[2], "total": r[3]} for r in rows]


def _ventas_por_cajero():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT u.nombre, COUNT(v.id_venta) as num_ventas,
               SUM(v.total) as total
        FROM ventas v
        JOIN usuarios u ON u.id_usuario = v.id_usuario
        WHERE v.estado = 'activa'
        GROUP BY v.id_usuario
        ORDER BY total DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [{"cajero": r[0], "ventas": r[1], "total": r[2]} for r in rows]


def _inventario_actual():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT codigo_producto, nombre, stock, stock_minimo, categoria,
               precio_venta, precio_compra
        FROM productos WHERE estado = 1
        ORDER BY nombre
    """)
    rows = c.fetchall()
    conn.close()
    return [{"codigo": r[0], "nombre": r[1], "stock": r[2],
             "stock_minimo": r[3], "categoria": r[4],
             "precio_venta": r[5], "precio_compra": r[6]} for r in rows]


def _ganancias_por_producto(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.codigo_producto, p.nombre,
               SUM(dv.cantidad) as unidades,
               SUM(dv.subtotal) as ingresos,
               SUM(dv.cantidad * p.precio_compra) as costo,
               SUM(dv.subtotal) - SUM(dv.cantidad * p.precio_compra) as ganancia
        FROM detalle_venta dv
        JOIN productos p ON p.id_producto = dv.id_producto
        JOIN ventas v ON v.id_venta = dv.id_venta
        WHERE v.estado = 'activa'
        GROUP BY dv.id_producto
        ORDER BY ganancia DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"codigo": r[0], "nombre": r[1], "unidades": r[2],
             "ingresos": r[3], "costo": r[4], "ganancia": r[5]} for r in rows]


def _resumen_financiero():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(SUM(total),0) FROM ventas
        WHERE date(fecha) = date('now') AND estado='activa'
    """)
    hoy = c.fetchone()[0]
    c.execute("""
        SELECT COALESCE(SUM(total),0) FROM ventas
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m','now') AND estado='activa'
    """)
    mes = c.fetchone()[0]
    c.execute("""
        SELECT COALESCE(SUM(v.total - (
            SELECT COALESCE(SUM(dv2.cantidad * p2.precio_compra),0)
            FROM detalle_venta dv2 JOIN productos p2 ON p2.id_producto = dv2.id_producto
            WHERE dv2.id_venta = v.id_venta
        )),0) FROM ventas v WHERE estado='activa'
    """)
    ganancia_total = c.fetchone()[0]
    conn.close()
    return {"hoy": hoy, "mes": mes, "ganancia_total": ganancia_total}


# ── vista ─────────────────────────────────────────────────────────────────────

def build_reports_view(page, user_data, nav):

    # Filtros de fecha
    f_desde = field("Desde (YYYY-MM-DD)", value="")
    f_hasta = field("Hasta (YYYY-MM-DD)", value="")

    content_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    # Tabs
    selected_tab = {"key": "ventas_hoy"}

    tab_keys = [
        ("ventas_hoy",    "Ventas Hoy"),
        ("ventas_periodo","Por Período"),
        ("productos",     "Prod. Más Vendidos"),
        ("stock_bajo",    "Stock Bajo"),
        ("clientes",      "Top Clientes"),
        ("cajeros",       "Por Cajero"),
        ("inventario",    "Inventario"),
        ("ganancias",     "Ganancias"),
        ("financiero",    "Resumen Financiero"),
    ]

    tabs_row = ft.Row(spacing=6, wrap=True)

    def build_tabs():
        tabs_row.controls.clear()
        for key, label in tab_keys:
            active = selected_tab["key"] == key
            tabs_row.controls.append(
                ft.Container(
                    height=36, border_radius=8, padding=psym(12, 0),
                    bgcolor=C["header"] if active else C["panel"],
                    border=ft.border.all(1, C["accent"] if active else C["border"]),
                    on_click=lambda _, k=key: switch_tab(k),
                    content=ft.Text(label, size=12, color=C["white"] if active else C["lgrey"],
                                    weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400),
                )
            )

    def switch_tab(key):
        selected_tab["key"] = key
        build_tabs()
        load_report()
        page.update()

    def _header_row(*labels):
        return ft.Row(controls=[
            ft.Text(l, size=11, color=C["grey"],
                    expand=(i == 0), weight=ft.FontWeight.W_600)
            for i, l in enumerate(labels)
        ])

    def _data_row(cols, colors=None):
        controls = []
        for i, (text, expand) in enumerate(cols):
            color = (colors[i] if colors and i < len(colors) else C["lgrey"])
            controls.append(ft.Text(str(text), size=12, color=color,
                                    expand=(i == 0)))
        return ft.Row(controls=controls)

    def load_report():
        content_col.controls.clear()
        key = selected_tab["key"]

        # ── Ventas Hoy ──────────────────────────────────────────
        if key == "ventas_hoy":
            rows = _ventas_diarias()
            total = sum(r["total"] for r in rows)
            content_col.controls += [
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"{len(rows)} ventas hoy", size=13, color=C["lgrey"]),
                        ft.Text(f"Total: ${total:.2f}", size=15,
                                color=C["green"], weight=ft.FontWeight.W_700),
                    ]
                ),
                _header_row("Fecha", "Cliente", "Cajero", "Método", "Total", "Factura"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin ventas hoy.", color=C["grey"]))
            for r in rows:
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["fecha"][5:16], size=12, color=C["lgrey"], expand=True),
                        ft.Text(r["cliente"][:18], size=12, color=C["text"]),
                        ft.Text(r["cajero"][:14],  size=12, color=C["lgrey"]),
                        status_chip(r["metodo"], C["header"]),
                        ft.Text(f"${r['total']:.2f}", size=12, color=C["green"],
                                weight=ft.FontWeight.W_600),
                        ft.Text(r["factura"] or "—", size=11, color=C["grey"]),
                    ])
                )

        # ── Ventas por Período ──────────────────────────────────
        elif key == "ventas_periodo":
            content_col.controls += [
                ft.Row(spacing=10, controls=[
                    f_desde, f_hasta,
                    primary_btn("Consultar", on_click=lambda _: _query_periodo()),
                ]),
                ft.Divider(color=C["border"], thickness=1),
            ]

        # ── Productos más vendidos ──────────────────────────────
        elif key == "productos":
            rows = _productos_mas_vendidos()
            content_col.controls += [
                _header_row("Código", "Producto", "Unidades", "Ingresos"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            for i, r in enumerate(rows):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(f"{medal} {r['codigo']}", size=12,
                                color=C["accent"], expand=True),
                        ft.Text(r["nombre"][:24], size=12, color=C["text"]),
                        ft.Text(str(r["unidades"]), size=12, color=C["lgrey"]),
                        ft.Text(f"${r['ingresos']:.2f}", size=12,
                                color=C["green"], weight=ft.FontWeight.W_600),
                    ])
                )
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin datos de ventas.", color=C["grey"]))

        # ── Stock bajo ───────────────────────────────────────────
        elif key == "stock_bajo":
            rows = get_low_stock_products()
            content_col.controls += [
                _header_row("Código", "Producto", "Stock", "Mínimo"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin productos con stock bajo.", color=C["grey"]))
            for r in rows:
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["codigo"], size=12, color=C["accent"], expand=True),
                        ft.Text(r["nombre"][:24], size=12, color=C["text"]),
                        ft.Text(str(r["stock"]), size=12, color=C["red"],
                                weight=ft.FontWeight.W_700),
                        ft.Text(str(r["stock_minimo"]), size=12, color=C["lgrey"]),
                    ])
                )

        # ── Top Clientes ────────────────────────────────────────
        elif key == "clientes":
            rows = _clientes_top()
            content_col.controls += [
                _header_row("Cliente", "Documento", "# Compras", "Total"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            for r in rows:
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["nombre"][:24], size=12, color=C["text"], expand=True),
                        ft.Text(r["documento"],   size=12, color=C["lgrey"]),
                        ft.Text(str(r["compras"]),size=12, color=C["lgrey"]),
                        ft.Text(f"${r['total']:.2f}", size=12, color=C["green"],
                                weight=ft.FontWeight.W_600),
                    ])
                )
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin datos.", color=C["grey"]))

        # ── Ventas por cajero ───────────────────────────────────
        elif key == "cajeros":
            rows = _ventas_por_cajero()
            content_col.controls += [
                _header_row("Cajero", "# Ventas", "Total"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            for r in rows:
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["cajero"], size=12, color=C["text"], expand=True),
                        ft.Text(str(r["ventas"]), size=12, color=C["lgrey"]),
                        ft.Text(f"${r['total']:.2f}", size=12, color=C["green"],
                                weight=ft.FontWeight.W_600),
                    ])
                )
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin datos.", color=C["grey"]))

        # ── Inventario actual ───────────────────────────────────
        elif key == "inventario":
            rows = _inventario_actual()
            content_col.controls += [
                ft.Text(f"{len(rows)} productos activos", size=12, color=C["lgrey"]),
                _header_row("Código", "Producto", "Stock", "Mín", "P.Venta", "Categoría"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            for r in rows:
                low = r["stock"] <= r["stock_minimo"]
                sc  = C["red"] if low else C["text"]
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["codigo"], size=12, color=C["accent"], expand=True),
                        ft.Text(r["nombre"][:22], size=12, color=C["text"]),
                        ft.Text(str(r["stock"]), size=12, color=sc,
                                weight=ft.FontWeight.W_700),
                        ft.Text(str(r["stock_minimo"]), size=12, color=C["lgrey"]),
                        ft.Text(f"${r['precio_venta']:.2f}", size=12, color=C["green"]),
                        ft.Text(r["categoria"] or "—", size=11, color=C["grey"]),
                    ])
                )
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin productos.", color=C["grey"]))

        # ── Ganancias por producto ──────────────────────────────
        elif key == "ganancias":
            rows = _ganancias_por_producto()
            content_col.controls += [
                _header_row("Código", "Producto", "Unid.", "Ingresos", "Costo", "Ganancia"),
                ft.Divider(color=C["border"], thickness=1),
            ]
            for r in rows:
                content_col.controls.append(
                    ft.Row(controls=[
                        ft.Text(r["codigo"], size=12, color=C["accent"], expand=True),
                        ft.Text(r["nombre"][:20], size=12, color=C["text"]),
                        ft.Text(str(r["unidades"]), size=12, color=C["lgrey"]),
                        ft.Text(f"${r['ingresos']:.2f}", size=12, color=C["lgrey"]),
                        ft.Text(f"${r['costo']:.2f}", size=12, color=C["red"]),
                        ft.Text(f"${r['ganancia']:.2f}", size=12, color=C["green"],
                                weight=ft.FontWeight.W_700),
                    ])
                )
            if not rows:
                content_col.controls.append(
                    ft.Text("Sin datos de ventas.", color=C["grey"]))

        # ── Resumen financiero ──────────────────────────────────
        elif key == "financiero":
            fin = _resumen_financiero()

            def fin_card(titulo, valor, color):
                return ft.Container(
                    expand=True, bgcolor=C["card"], border_radius=12,
                    border=ft.border.all(1, C["border"]), padding=pall(16),
                    content=ft.Column(spacing=8, controls=[
                        ft.Text(titulo, size=12, color=C["grey"]),
                        ft.Text(f"${valor:.2f}", size=30,
                                weight=ft.FontWeight.W_700, color=color),
                    ]),
                )

            content_col.controls.append(
                ft.Row(spacing=12, controls=[
                    fin_card("Ingresos hoy",        fin["hoy"],           C["accent"]),
                    fin_card("Ingresos este mes",   fin["mes"],           C["green"]),
                    fin_card("Ganancia acumulada",  fin["ganancia_total"],C["yellow"]),
                ])
            )

        page.update()

    # ── consulta período con feedback ──────────────────────────
    periodo_col = ft.Column(spacing=6)

    def _query_periodo():
        desde = f_desde.value.strip()
        hasta = f_hasta.value.strip()
        if not desde or not hasta:
            show_snack(page, "Ingresa fechas válidas (YYYY-MM-DD)", False)
            return
        rows = _ventas_por_periodo(desde, hasta)
        periodo_col.controls.clear()
        total = sum(r["total"] for r in rows)
        periodo_col.controls += [
            ft.Text(f"{len(rows)} ventas | Total: ${total:.2f}",
                    size=13, color=C["green"], weight=ft.FontWeight.W_600),
            ft.Divider(color=C["border"], thickness=1),
        ]
        if not rows:
            periodo_col.controls.append(
                ft.Text("Sin ventas en ese período.", color=C["grey"]))
        for r in rows:
            periodo_col.controls.append(
                ft.Row(controls=[
                    ft.Text(r["fecha"][:16], size=12, color=C["lgrey"], expand=True),
                    ft.Text(r["cliente"][:18], size=12, color=C["text"]),
                    ft.Text(r["cajero"][:14],  size=12, color=C["lgrey"]),
                    status_chip(r["metodo"], C["header"]),
                    ft.Text(f"${r['total']:.2f}", size=12, color=C["green"],
                            weight=ft.FontWeight.W_600),
                ])
            )
        # agregar tabla de período dentro del content_col
        if len(content_col.controls) < 3:
            content_col.controls.append(periodo_col)
        page.update()

    body = [
        card(ft.Column(spacing=12, controls=[
            section_title("Reportes del Sistema"),
            tabs_row,
            ft.Divider(color=C["border"], thickness=1),
            content_col,
        ])),
    ]

    build_tabs()
    render_page(page, "reportes", nav, user_data, body)
    load_report()
