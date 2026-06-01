import flet as ft

from app.repositories.products_repository import get_low_stock_products
from app.services.inventory_service import (
    get_metrics, get_recent_movements, register_movement,
)
from app.views.shared import (
    C, card, field, pall, primary_btn, render_page, section_title,
    show_snack, status_chip,
)


def build_inventory_view(page, user_data, nav):
    actor = user_data["usuario"]
    allow_movement = user_data.get("rol") == "administrador"

    f_cod  = field("Código producto*")
    f_type = field("Tipo: entrada | salida | ajuste", value="entrada")
    f_qty  = field("Cantidad*")
    f_mot  = field("Motivo (opcional)")

    mov_col = ft.Column(spacing=6)
    low_col = ft.Column(spacing=4)

    def load_movements():
        mov_col.controls.clear()
        for m in get_recent_movements(25):
            color = (C["green"] if m["tipo"] == "entrada"
                     else C["red"] if m["tipo"] == "salida"
                     else C["orange"])
            mov_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(f"{m['codigo']}  –  {m['nombre']}",
                                        size=13, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Motivo: {m['motivo'] or '—'}  |  "
                                    f"Usuario: {m['usuario'] or '—'}  |  "
                                    f"{m['fecha'][:16]}",
                                    size=11, color=C["lgrey"],
                                ),
                            ]),
                            ft.Row(spacing=8, controls=[
                                status_chip(m["tipo"].capitalize(), color),
                                ft.Text(
                                    f"±{m['cantidad']}",
                                    size=13, color=color,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.Text(
                                    f"→ {m['stock_nuevo']}",
                                    size=12, color=C["lgrey"],
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def load_low():
        low_col.controls.clear()
        lows = get_low_stock_products()
        if not lows:
            low_col.controls.append(
                ft.Text("Todos los productos tienen stock suficiente ✓",
                        color=C["green"], size=12))
        for p in lows:
            low_col.controls.append(
                ft.Container(
                    bgcolor="#2B2418", border_radius=8,
                    border=ft.border.all(1, C["orange"]), padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{p['codigo']}  –  {p['nombre']}",
                                    size=13, color=C["yellow"],
                                    weight=ft.FontWeight.W_600),
                            ft.Text(
                                f"Stock: {p['stock']}  /  Mín: {p['stock_minimo']}",
                                size=12, color=C["yellow"],
                            ),
                        ],
                    ),
                )
            )
        page.update()

    def do_movement(_):
        if not allow_movement:
            show_snack(page, "No tienes permisos para registrar movimientos", False)
            return
        try:
            register_movement(
                product_code=f_cod.value,
                mov_type=f_type.value,
                quantity=f_qty.value,
                reason=f_mot.value,
                username=actor,
            )
            show_snack(page, "Movimiento registrado correctamente")
            for f in [f_cod, f_qty, f_mot]:
                f.value = ""
            f_type.value = "entrada"
            load_movements()
            load_low()
        except ValueError as e:
            show_snack(page, str(e), False)

    metrics = get_metrics()

    def metric_card(title, value, color):
        return ft.Container(
            expand=True, bgcolor=C["card"], border_radius=12,
            border=ft.border.all(1, C["border"]), padding=pall(14),
            content=ft.Column(spacing=8, controls=[
                ft.Text(title, size=12, color=C["grey"]),
                ft.Text(str(value), size=32, weight=ft.FontWeight.W_700,
                        color=color),
            ]),
        )

    body = [
        ft.Row(spacing=12, controls=[
            metric_card("Productos activos", metrics["total_products"], C["accent"]),
            metric_card("Stock bajo",        metrics["low_stock"],
                        C["red"] if metrics["low_stock"] > 0 else C["grey"]),
            metric_card("Movimientos hoy",   metrics["movements_today"], C["orange"]),
        ]),
    ]
    if allow_movement:
        body.append(
            card(ft.Column(spacing=10, controls=[
                section_title("Registrar Movimiento"),
                ft.Row(spacing=10, controls=[f_cod, f_type]),
                ft.Row(spacing=10, controls=[f_qty, f_mot]),
                primary_btn("Registrar movimiento", on_click=do_movement),
            ]))
        )
    body += [
        card(ft.Column(spacing=10, controls=[
            section_title("Alertas de Stock Bajo"),
            ft.Divider(color=C["border"], thickness=1),
            low_col,
        ])),
        card(ft.Column(spacing=10, controls=[
            section_title("Últimos Movimientos"),
            ft.Divider(color=C["border"], thickness=1),
            mov_col,
        ])),
    ]
    render_page(page, "inventario", nav, user_data, body)
    load_movements()
    load_low()
