import flet as ft

from app.repositories.invoices_repository import get_invoice_info, list_invoices
from app.services.invoice_service import annul_invoice
from app.services.sales_service import get_items_for_sale
from app.views.shared import (
    C, card, pall, render_page, section_title, show_snack, status_chip,
)


def build_invoices_view(page, user_data, nav):
    actor = user_data["usuario"]
    invoices_col = ft.Column(spacing=6)
    detail_col   = ft.Column(spacing=4)
    detail_title = ft.Text("", size=14, color=C["text"], weight=ft.FontWeight.W_700)

    def build_invoice_text(info, items):
        lines = [
            f"Factura: {info['numero']}",
            f"Fecha: {info['fecha'][:16]}",
            f"Cliente: {info['cliente']}",
            f"Método: {info['metodo_pago']}",
            "",
            "Producto | Cant. | P/U | Subtotal",
        ]
        for it in items:
            lines.append(
                f"{it['nombre']} | {it['cantidad']} | ${it['precio']:.2f} | ${it['subtotal']:.2f}"
            )
        lines += [
            "",
            f"Subtotal: ${info['subtotal']:.2f}",
            f"Impuestos: ${info['impuestos']:.2f}",
            f"Total: ${info['total']:.2f}",
        ]
        return "\n".join(lines)

    def load_invoices():
        invoices_col.controls.clear()
        invoices = list_invoices(30)
        if not invoices:
            invoices_col.controls.append(
                ft.Text("No hay facturas registradas.", color=C["grey"]))
        for inv in invoices:
            status_color = C["green"] if inv["estado"] == "activa" else C["grey"]
            invoices_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(f"{inv['numero']}",
                                        size=13, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Cliente: {inv['cliente']}  |  "
                                    f"Fecha: {inv['fecha'][:16]}",
                                    size=11, color=C["lgrey"],
                                ),
                            ]),
                            ft.Row(spacing=8, controls=[
                                status_chip(inv["estado"].capitalize(), status_color),
                                ft.Text(f"${inv['total']:.2f}",
                                        size=14, color=C["green"],
                                        weight=ft.FontWeight.W_700),
                                ft.IconButton(
                                    ft.Icons.RECEIPT_LONG_OUTLINED,
                                    icon_size=18, icon_color=C["accent"],
                                    tooltip="Ver detalle",
                                    on_click=lambda _, inv=inv: show_detail(inv),
                                ),
                                ft.IconButton(
                                    ft.Icons.PRINT_OUTLINED,
                                    icon_size=18, icon_color=C["accent"],
                                    tooltip="Imprimir factura",
                                    on_click=lambda _, inv=inv: do_print(inv),
                                ),
                                ft.IconButton(
                                    ft.Icons.CANCEL_OUTLINED,
                                    icon_size=18, icon_color=C["red"],
                                    tooltip="Anular factura",
                                    disabled=inv["estado"] != "activa",
                                    on_click=lambda _, inv=inv: do_annul(inv),
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def do_print(inv):
        info = get_invoice_info(inv["id"])
        if not info:
            show_snack(page, "Factura no encontrada", False)
            return
        items = get_items_for_sale(info["id_venta"])
        text = build_invoice_text(info, items)
        page.set_clipboard(text)
        show_snack(page, "Factura copiada al portapapeles")

    def do_annul(inv):
        try:
            info = annul_invoice(inv["id"], actor)
            show_snack(page, f"Factura {info['numero']} anulada")
            load_invoices()
            detail_col.controls.clear()
            detail_title.value = ""
            page.update()
        except ValueError as e:
            show_snack(page, str(e), False)

    def show_detail(inv):
        detail_col.controls.clear()
        detail_title.value = f"Detalle – {inv['numero']}"
        info = get_invoice_info(inv["id"])
        if not info:
            detail_col.controls.append(
                ft.Text("Factura no encontrada.", color=C["grey"]))
            page.update()
            return

        items = get_items_for_sale(info["id_venta"])

        if not items:
            detail_col.controls.append(
                ft.Text("Sin detalle disponible.", color=C["grey"]))
        else:
            detail_col.controls.append(
                ft.Row(controls=[
                    ft.Text("Producto", size=11, color=C["grey"], expand=True),
                    ft.Text("Cant.", size=11, color=C["grey"]),
                    ft.Text("P/U", size=11, color=C["grey"]),
                    ft.Text("Subtotal", size=11, color=C["grey"]),
                ])
            )
            detail_col.controls.append(
                ft.Divider(color=C["border"], thickness=1))
            for it in items:
                detail_col.controls.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(it["nombre"], size=12,
                                    color=C["text"], expand=True),
                            ft.Text(str(it["cantidad"]), size=12, color=C["lgrey"]),
                            ft.Text(f"${it['precio']:.2f}", size=12, color=C["lgrey"]),
                            ft.Text(f"${it['subtotal']:.2f}", size=12,
                                    color=C["green"],
                                    weight=ft.FontWeight.W_600),
                        ],
                    )
                )
            detail_col.controls.append(ft.Divider(color=C["border"], thickness=1))
            detail_col.controls.append(
                ft.Row(alignment=ft.MainAxisAlignment.END, controls=[
                    ft.Text(f"Total:  ${info['total']:.2f}",
                            size=14, color=C["green"],
                            weight=ft.FontWeight.W_700),
                ])
            )
        page.update()

    body = [
        card(ft.Column(spacing=10, controls=[
            section_title("Facturas Generadas"),
            ft.Divider(color=C["border"], thickness=1),
            invoices_col,
        ])),
        card(ft.Column(spacing=8, controls=[
            detail_title,
            detail_col,
        ])),
    ]
    render_page(page, "facturas", nav, user_data, body)
    load_invoices()
