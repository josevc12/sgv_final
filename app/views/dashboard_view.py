import flet as ft

from app.repositories.products_repository import get_low_stock_products
from app.services.inventory_service import get_metrics
from app.services.sales_service import get_all_sales
from app.services.backup_service import create_backup
from app.views.shared import (
    C, card, pall, primary_btn, psym, render_page, section_title, show_snack, status_chip,
)


def build_dashboard_view(page, user_data, nav):
    metrics = get_metrics()
    low     = get_low_stock_products()
    sales   = get_all_sales(5)
    is_admin = user_data.get("rol") == "administrador"

    def do_backup(_):
        try:
            path = create_backup()
            show_snack(page, f"Respaldo creado: {path}")
        except Exception as e:
            show_snack(page, f"Error al crear respaldo: {e}", False)

    def stat_card(title, value, color, icon):
        return ft.Container(
            expand=True, bgcolor=C["card"], border_radius=12,
            border=ft.border.all(1, C["border"]), padding=pall(16),
            content=ft.Column(spacing=10, controls=[
                ft.Row(spacing=6, controls=[
                    ft.Icon(icon, size=18, color=color),
                    ft.Text(title, size=12, color=C["grey"]),
                ]),
                ft.Text(str(value), size=34,
                        weight=ft.FontWeight.W_700, color=color),
            ]),
        )

    # Fila de métricas
    stats_row = ft.Row(spacing=12, controls=[
        stat_card("Productos activos", metrics["total_products"],
                  C["accent"], ft.Icons.INVENTORY_2_OUTLINED),
        stat_card("Stock bajo",        metrics["low_stock"],
                  C["red"] if metrics["low_stock"] > 0 else C["grey"],
                  ft.Icons.WARNING_AMBER_ROUNDED),
        stat_card("Movimientos hoy",   metrics["movements_today"],
                  C["orange"], ft.Icons.SWAP_VERT),
        stat_card("Últimas ventas",    len(sales),
                  C["green"], ft.Icons.POINT_OF_SALE),
    ])

    # Alerta stock bajo
    alert = ft.Container(
        bgcolor="#2B2418", border_radius=10,
        border=ft.border.all(1, C["orange"]), padding=pall(12),
        visible=len(low) > 0,
        content=ft.Column(spacing=6, controls=[
            ft.Row(spacing=8, controls=[
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=C["orange"], size=18),
                ft.Text(f"{len(low)} producto(s) con stock bajo — revisa Inventario",
                        size=13, color=C["yellow"], weight=ft.FontWeight.W_600),
            ]),
            *[
                ft.Text(
                    f"  • {p['nombre']}  (stock: {p['stock']} / mín: {p['stock_minimo']})",
                    size=12, color=C["yellow"],
                )
                for p in low[:5]
            ],
        ]),
    ) if low else ft.Container(height=0)

    # Tabla ventas recientes
    sale_rows = [
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Text(s["fecha"][:16], size=12, color=C["lgrey"], expand=True),
            ft.Text(s["cliente"],    size=12, color=C["lgrey"], expand=True),
            ft.Text(s["cajero"],     size=12, color=C["lgrey"], expand=True),
            ft.Text(f"${s['total']:.2f}", size=12, color=C["green"],
                    weight=ft.FontWeight.W_700),
            status_chip(s["metodo"], C["header"]),
            ft.Text(s["factura"] or "—", size=11, color=C["grey"]),
        ])
        for s in sales
    ] or [ft.Text("Sin ventas registradas.", color=C["grey"])]

    body = [
        stats_row,
        ft.Row(spacing=8, controls=[
            primary_btn("Crear respaldo", on_click=do_backup, color=C["header"],
                        expand=False),
        ]) if is_admin else ft.Container(height=0),
        alert,
        card(ft.Column(spacing=10, controls=[
            section_title("Últimas ventas"),
            ft.Row(controls=[
                ft.Text("Fecha",    size=11, color=C["grey"], expand=True),
                ft.Text("Cliente",  size=11, color=C["grey"], expand=True),
                ft.Text("Cajero",   size=11, color=C["grey"], expand=True),
                ft.Text("Total",    size=11, color=C["grey"]),
                ft.Text("Método",   size=11, color=C["grey"]),
                ft.Text("Factura",  size=11, color=C["grey"]),
            ]),
            ft.Divider(color=C["border"], thickness=1),
            *sale_rows,
        ])),
    ]
    render_page(page, "dashboard", nav, user_data, body)
