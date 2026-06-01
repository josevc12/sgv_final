import flet as ft

from app.repositories.caja_repository import get_open_caja
from app.services.client_service import get_all_clients
from app.services.product_service import find_product_for_sale
from app.services.sales_service import confirm_sale
from app.views.shared import (
    C, card, field, pall, psym, primary_btn, render_page,
    section_title, show_snack, status_chip,
)

METHODS = ["efectivo", "tarjeta", "transferencia", "mixto"]


def build_pos_view(page, user_data, nav):
    cart   = []   # [{id_producto, nombre, cantidad, precio_unitario}]
    state  = {"id_cliente": 1, "metodo": "efectivo"}

    # ── Campos búsqueda ────────────────────────────────────────────────────────
    f_code = field("Código o nombre del producto…")
    f_qty  = field("Cantidad", value="1", width=90)

    # ── Selector de cliente ────────────────────────────────────────────────────
    clients     = get_all_clients()
    client_opts = [ft.dropdown.Option(str(cl["id"]), cl["nombre"])
                   for cl in clients]
    dd_client   = ft.Dropdown(
        options=client_opts,
        value="1",
        border_color=C["border"],
        focused_border_color=C["accent"],
        bgcolor=C["panel"], color=C["white"],
        text_size=13, height=44,
    )
    dd_client.on_change = lambda e: state.update({"id_cliente": int(e.control.value)})

    # ── Selector método de pago ────────────────────────────────────────────────
    dd_method = ft.Dropdown(
        options=[ft.dropdown.Option(m, m.capitalize()) for m in METHODS],
        value="efectivo",
        border_color=C["border"],
        focused_border_color=C["accent"],
        bgcolor=C["panel"], color=C["white"],
        text_size=13, height=44,
    )
    dd_method.on_change = lambda e: state.update({"metodo": e.control.value})

    # ── Contenedor del carrito ─────────────────────────────────────────────────
    cart_col   = ft.Column(spacing=6)
    total_text = ft.Text("Total: $0.00", size=22,
                         color=C["accent"], weight=ft.FontWeight.W_700)
    sub_text   = ft.Text("Subtotal: $0.00  |  IVA (19%): $0.00",
                         size=12, color=C["grey"])
    result_box = ft.Container(visible=False, bgcolor=C["panel"],
                              border_radius=10, padding=pall(14),
                              content=ft.Column(spacing=4))

    # Advertencia de caja cerrada (visible solo cuando aplica)
    caja_warning = ft.Container(
        visible=False,
        bgcolor="#2A1A00",
        border_radius=8,
        padding=pall(10),
        content=ft.Row(spacing=8, controls=[
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=C["yellow"], size=18),
            ft.Text(
                "No tienes una caja abierta. La venta se registrará igualmente.",
                size=12, color=C["yellow"],
            ),
        ]),
    )

    def check_caja_warning():
        """Muestra o esconde la advertencia según si hay caja abierta."""
        abierta = get_open_caja(user_data["id_usuario"])
        caja_warning.visible = not abierta
        page.update()

    def refresh_totals():
        sub   = sum(i["cantidad"] * i["precio_unitario"] for i in cart)
        iva   = round(sub * 0.19, 2)
        total = round(sub + iva, 2)
        sub_text.value   = f"Subtotal: ${sub:.2f}  |  IVA (19%): ${iva:.2f}"
        total_text.value = f"Total: ${total:.2f}"

    def refresh_cart():
        cart_col.controls.clear()
        if not cart:
            cart_col.controls.append(
                ft.Text("Carrito vacío. Busca y agrega productos.",
                        color=C["grey"], size=13))
        else:
            for idx, item in enumerate(cart):
                subtotal = item["cantidad"] * item["precio_unitario"]
                cart_col.controls.append(
                    ft.Container(
                        bgcolor=C["panel"], border_radius=8, padding=pall(10),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=2, expand=True, controls=[
                                    ft.Text(item["nombre"], size=13, color=C["text"],
                                            weight=ft.FontWeight.W_600),
                                    ft.Text(
                                        f"Cant: {item['cantidad']}  ×  "
                                        f"${item['precio_unitario']:.2f}  =  "
                                        f"${subtotal:.2f}",
                                        size=11, color=C["lgrey"],
                                    ),
                                ]),
                                ft.IconButton(
                                    ft.Icons.DELETE_OUTLINE, icon_size=18,
                                    icon_color=C["red"],
                                    on_click=lambda _, i=idx: remove_item(i),
                                ),
                            ],
                        ),
                    )
                )
        refresh_totals()
        page.update()

    def remove_item(idx):
        cart.pop(idx)
        refresh_cart()

    def add_to_cart(_):
        code = f_code.value.strip().upper()
        if not code:
            show_snack(page, "Ingresa el código del producto", False); return
        try:
            qty = int(f_qty.value or "1")
            if qty <= 0: raise ValueError()
        except ValueError:
            show_snack(page, "Cantidad inválida", False); return

        product, err = find_product_for_sale(code)
        if not product:
            if err == "multiple":
                show_snack(page, "Hay varios productos con ese nombre. Usa el código.", False)
            else:
                show_snack(page, f"Producto '{code}' no encontrado", False)
            return
        if product["stock"] < qty:
            show_snack(page, f"Stock insuficiente (disponible: {product['stock']})", False)
            return

        # Si ya está en el carrito, sumar cantidad
        for item in cart:
            if item["id_producto"] == product["id"]:
                item["cantidad"] += qty
                break
        else:
            cart.append({
                "id_producto":     product["id"],
                "nombre":          product["nombre"],
                "cantidad":        qty,
                "precio_unitario": product["precio_venta"],
            })

        f_code.value = ""
        f_qty.value  = "1"
        refresh_cart()
        show_snack(page, f"'{product['nombre']}' agregado al carrito")

    f_code.on_submit = add_to_cart

    def do_sale(_):
        if not cart:
            show_snack(page, "El carrito está vacío", False)
            return

        # CORRECCIÓN: ya no bloquea si no hay caja abierta.
        # Solo advierte con el banner amarillo pero permite continuar.
        try:
            result = confirm_sale(
                id_usuario  = user_data["id_usuario"],
                id_cliente  = state["id_cliente"],
                items       = cart,
                metodo_pago = state["metodo"],
                username    = user_data["usuario"],
            )
            # Mostrar resumen de venta exitosa
            result_box.content.controls.clear()
            result_box.content.controls += [
                ft.Row(spacing=6, controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=C["green"], size=20),
                    ft.Text("Venta confirmada", size=15,
                            color=C["green"], weight=ft.FontWeight.W_700),
                ]),
                ft.Text(f"Factura: {result['numero_factura']}",
                        size=13, color=C["text"]),
                ft.Text(
                    f"Subtotal: ${result['subtotal']:.2f}  |  "
                    f"IVA: ${result['impuestos']:.2f}  |  "
                    f"Total: ${result['total']:.2f}",
                    size=13, color=C["lgrey"],
                ),
            ]
            result_box.visible = True
            cart.clear()
            refresh_cart()
        except ValueError as e:
            show_snack(page, str(e), False)

    def clear_cart(_):
        cart.clear()
        result_box.visible = False
        refresh_cart()

    body = [
        caja_warning,
        ft.Row(spacing=14, controls=[
            # Panel izquierdo – carrito
            ft.Container(expand=2, content=card(ft.Column(spacing=10, controls=[
                section_title("Carrito de Venta"),
                ft.Row(spacing=8, controls=[
                    f_code, f_qty,
                    primary_btn("Agregar", on_click=add_to_cart),
                ]),
                ft.Divider(color=C["border"], thickness=1),
                cart_col,
            ]))),
            # Panel derecho – resumen y confirmar
            ft.Container(expand=1, content=card(ft.Column(spacing=12, controls=[
                section_title("Resumen"),
                ft.Text("Cliente", size=11, color=C["grey"], weight=ft.FontWeight.W_600),
                dd_client,
                ft.Text("Método de pago", size=11, color=C["grey"],
                        weight=ft.FontWeight.W_600),
                dd_method,
                ft.Divider(color=C["border"], thickness=1),
                sub_text,
                total_text,
                ft.Container(height=4),
                primary_btn("✓  Confirmar Venta", on_click=do_sale,
                            color=C["green"], expand=True),
                primary_btn("Limpiar carrito", on_click=clear_cart,
                            color=C["red"], expand=True),
                result_box,
            ]))),
        ]),
    ]
    render_page(page, "pos", nav, user_data, body)
    refresh_cart()
    check_caja_warning()