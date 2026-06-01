import flet as ft

from app.db.connection import get_connection
from app.repositories.audit_repository import log_event
from app.views.shared import (
    C, card, field, pall, psym, primary_btn, render_page,
    section_title, show_snack, status_chip,
)


# ── helpers DB ────────────────────────────────────────────────────────────────

def _get_open_caja(id_usuario):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_caja, monto_inicial, fecha_apertura
        FROM caja WHERE id_usuario = ? AND estado = 'abierta'
        ORDER BY id_caja DESC LIMIT 1
    """, (id_usuario,))
    row = c.fetchone()
    conn.close()
    return row  # (id_caja, monto_inicial, fecha_apertura) | None


def _open_caja(id_usuario, monto_inicial, username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO caja (id_usuario, monto_inicial, estado)
        VALUES (?,?,'abierta')
    """, (id_usuario, monto_inicial))
    conn.commit()
    conn.close()
    log_event("caja_abierta", username, f"Monto inicial: ${monto_inicial:.2f}")


def _close_caja(id_caja, id_usuario, username):
    conn = get_connection()
    c = conn.cursor()
    # ventas del turno (desde apertura)
    c.execute("""
        SELECT ca.fecha_apertura FROM caja ca WHERE ca.id_caja = ?
    """, (id_caja,))
    apertura = c.fetchone()[0]

    c.execute("""
        SELECT COALESCE(SUM(v.total),0),
               COALESCE(SUM(CASE WHEN v.metodo_pago='efectivo'   THEN v.total ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN v.metodo_pago='tarjeta'    THEN v.total ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN v.metodo_pago='transferencia' THEN v.total ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN v.metodo_pago='mixto'      THEN v.total ELSE 0 END),0),
               COUNT(*)
        FROM ventas v
        WHERE v.id_usuario = ? AND v.fecha >= ? AND v.estado = 'activa'
    """, (id_usuario, apertura))
    row = c.fetchone()
    total, efec, tarj, tran, mixt, num = row

    c.execute("""
        UPDATE caja SET estado='cerrada', fecha_cierre=datetime('now'), total_ventas=?
        WHERE id_caja=?
    """, (total, id_caja))
    conn.commit()
    conn.close()
    log_event("caja_cerrada", username, f"Total ventas: ${total:.2f} | {num} ventas")
    return {
        "total": total, "efectivo": efec, "tarjeta": tarj,
        "transferencia": tran, "mixto": mixt, "num_ventas": num,
    }


def _get_historial(id_usuario, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id_caja, fecha_apertura, fecha_cierre,
               monto_inicial, total_ventas, estado
        FROM caja WHERE id_usuario = ?
        ORDER BY id_caja DESC LIMIT ?
    """, (id_usuario, limit))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "apertura": r[1], "cierre": r[2],
             "inicial": r[3], "ventas": r[4], "estado": r[5]} for r in rows]


# ── vista ─────────────────────────────────────────────────────────────────────

def build_caja_view(page, user_data, nav):
    uid      = user_data["id_usuario"]
    username = user_data["usuario"]

    f_monto = field("Monto inicial ($)*")
    f_contado = field("Monto contado en caja ($)")

    status_col  = ft.Column(spacing=8)
    resumen_col = ft.Column(spacing=6)
    hist_col    = ft.Column(spacing=6)

    open_state = {"caja": None}   # guarda row abierta

    def refresh():
        status_col.controls.clear()
        resumen_col.controls.clear()

        row = _get_open_caja(uid)
        open_state["caja"] = row

        if row:
            id_caja, monto_ini, fecha_ap = row
            status_col.controls += [
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.LOCK_OPEN_OUTLINED, color=C["green"], size=22),
                    ft.Text("Caja ABIERTA", size=16, color=C["green"],
                            weight=ft.FontWeight.W_700),
                ]),
                ft.Text(f"Apertura: {fecha_ap[:16]}",
                        size=12, color=C["lgrey"]),
                ft.Text(f"Monto inicial: ${monto_ini:.2f}",
                        size=12, color=C["lgrey"]),
            f_contado,
                ft.Container(height=6),
                primary_btn("🔒  Cerrar Caja", on_click=do_close,
                            color=C["red"], expand=True),
            ]
        else:
            status_col.controls += [
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINED, color=C["grey"], size=22),
                    ft.Text("Caja CERRADA", size=16, color=C["grey"],
                            weight=ft.FontWeight.W_700),
                ]),
                ft.Container(height=6),
                f_monto,
                ft.Container(height=4),
                primary_btn("🔓  Abrir Caja", on_click=do_open,
                            color=C["green"], expand=True),
            ]

        load_hist()
        page.update()

    def do_open(_):
        try:
            monto = float(f_monto.value or "0")
            if monto < 0:
                raise ValueError()
        except ValueError:
            show_snack(page, "Ingresa un monto inicial válido", False)
            return
        if _get_open_caja(uid):
            show_snack(page, "Ya tienes una caja abierta", False)
            return
        _open_caja(uid, monto, username)
        f_monto.value = ""
        show_snack(page, f"Caja abierta con ${monto:.2f}")
        refresh()

    def do_close(_):
        row = open_state["caja"]
        if not row:
            show_snack(page, "No hay caja abierta", False)
            return
        id_caja = row[0]
        monto_ini = row[1]
        result = _close_caja(id_caja, uid, username)

        resumen_col.controls.clear()
        total_esperado = monto_ini + result["efectivo"]
        contado = None
        if f_contado.value.strip():
            try:
                contado = float(f_contado.value)
            except ValueError:
                show_snack(page, "Monto contado inválido", False)
                return
        if contado is None:
            contado = total_esperado
        diferencia = contado - total_esperado

        def res_row(label, value, color=None):
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(label, size=13, color=C["lgrey"]),
                    ft.Text(f"${value:.2f}", size=13,
                            color=color or C["text"],
                            weight=ft.FontWeight.W_600),
                ],
            )

        resumen_col.controls += [
            section_title("Resumen de Cierre", 14),
            ft.Divider(color=C["border"], thickness=1),
            ft.Text(f"Ventas realizadas: {result['num_ventas']}",
                    size=12, color=C["lgrey"]),
            res_row("Total ventas",        result["total"],        C["green"]),
            res_row("Efectivo",            result["efectivo"]),
            res_row("Tarjeta",             result["tarjeta"]),
            res_row("Transferencia",       result["transferencia"]),
            res_row("Mixto",               result["mixto"]),
            ft.Divider(color=C["border"], thickness=1),
            res_row("Monto inicial caja",  monto_ini),
            res_row("Total esperado (ef.)", monto_ini + result["efectivo"], C["accent"]),
            res_row("Monto contado",        contado),
            res_row("Diferencia",           diferencia,
                    C["green"] if diferencia >= 0 else C["red"]),
        ]

        show_snack(page, "Caja cerrada correctamente")
        open_state["caja"] = None
        f_contado.value = ""
        refresh()

    def load_hist():
        hist_col.controls.clear()
        for h in _get_historial(uid):
            abierta = h["estado"] == "abierta"
            hist_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(f"Apertura: {(h['apertura'] or '')[:16]}",
                                        size=12, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Cierre: {(h['cierre'] or '—')[:16]}  |  "
                                    f"Inicial: ${h['inicial'] or 0:.2f}  |  "
                                    f"Ventas: ${h['ventas'] or 0:.2f}",
                                    size=11, color=C["lgrey"],
                                ),
                            ]),
                            status_chip(
                                "Abierta" if abierta else "Cerrada",
                                C["green"] if abierta else C["grey"],
                            ),
                        ],
                    ),
                )
            )
        page.update()

    body = [
        ft.Row(spacing=14, controls=[
            ft.Container(expand=1, content=card(ft.Column(
                spacing=10, controls=[
                    section_title("Control de Caja"),
                    ft.Divider(color=C["border"], thickness=1),
                    status_col,
                    ft.Container(height=6),
                    resumen_col,
                ]
            ))),
            ft.Container(expand=1, content=card(ft.Column(
                spacing=10, controls=[
                    section_title("Historial de Cajas"),
                    ft.Divider(color=C["border"], thickness=1),
                    hist_col,
                ]
            ))),
        ]),
    ]
    render_page(page, "caja", nav, user_data, body)
    refresh()
