import flet as ft

from app.services.product_service import (
    activate_product, deactivate_product, edit_product,
    get_all_products, register_product,
)
from app.views.shared import (
    C, card, field, pall, primary_btn, render_page, section_title,
    show_snack, small_label, status_chip,
)


def build_products_view(page, user_data, nav):
    actor = user_data["usuario"]

    # ── Campos nuevo producto ──────────────────────────────────────────────────
    f_cod  = field("Código* (ej: PRD-001)")
    f_nom  = field("Nombre*")
    f_pcom = field("Precio compra*")
    f_pven = field("Precio venta*")
    f_st   = field("Stock inicial*")
    f_sm   = field("Stock mínimo*")
    f_cat  = field("Categoría")
    f_desc = field("Descripción")

    # ── Lista de resultados ────────────────────────────────────────────────────
    results_col  = ft.Column(spacing=6)
    edit_form    = ft.Column(spacing=8, visible=False)
    editing      = {"id": None}

    f_e_nom  = field("Nombre*")
    f_e_pcom = field("Precio compra*")
    f_e_pven = field("Precio venta*")
    f_e_sm   = field("Stock mínimo*")
    f_e_cat  = field("Categoría")

    def load_list(q=""):
        results_col.controls.clear()
        prods = get_all_products(search=q, only_active=False)
        if not prods:
            results_col.controls.append(
                ft.Text("Sin resultados.", color=C["grey"]))
        for p in prods:
            active    = p["estado"] == 1
            low_stock = p["stock"] <= p["stock_minimo"]
            sc        = C["red"] if low_stock else C["lgrey"]
            results_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(
                                    f"{p['codigo']}  –  {p['nombre']}",
                                    size=13, color=C["text"] if active else C["grey"],
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    f"Venta: ${p['precio_venta']:.2f}  |  "
                                    f"Compra: ${p['precio_compra']:.2f}  |  "
                                    f"Stock: {p['stock']}  |  "
                                    f"Cat: {p['categoria'] or '—'}",
                                    size=11, color=sc,
                                ),
                            ]),
                            ft.Row(spacing=6, controls=[
                                status_chip("Activo" if active else "Inactivo",
                                            C["green"] if active else C["grey"]),
                                ft.IconButton(
                                    ft.Icons.EDIT_OUTLINED, icon_size=18,
                                    icon_color=C["accent"],
                                    on_click=lambda _, p=p: open_edit(p),
                                ),
                                ft.IconButton(
                                    ft.Icons.TOGGLE_OFF if active else ft.Icons.TOGGLE_ON,
                                    icon_size=18,
                                    icon_color=C["red"] if active else C["green"],
                                    on_click=lambda _, p=p: toggle(p),
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def open_edit(p):
        editing["id"] = p["id"]
        f_e_nom.value  = p["nombre"]
        f_e_pcom.value = str(p["precio_compra"])
        f_e_pven.value = str(p["precio_venta"])
        f_e_sm.value   = str(p["stock_minimo"])
        f_e_cat.value  = p["categoria"]
        edit_form.visible = True
        page.update()

    def save_edit(_):
        try:
            edit_product(editing["id"], f_e_nom.value, f_e_pcom.value,
                         f_e_pven.value, f_e_sm.value, f_e_cat.value, actor)
            show_snack(page, "Producto actualizado")
            edit_form.visible = False
            load_list(f_search.value)
        except ValueError as e:
            show_snack(page, str(e), False)

    def cancel_edit(_):
        edit_form.visible = False
        page.update()

    def toggle(p):
        if p["estado"] == 1:
            deactivate_product(p["id"], actor)
        else:
            activate_product(p["id"], actor)
        load_list(f_search.value)

    edit_form.controls = [
        section_title("Editar producto", 14),
        ft.Row(spacing=10, controls=[f_e_nom, f_e_pcom, f_e_pven]),
        ft.Row(spacing=10, controls=[f_e_sm, f_e_cat]),
        ft.Row(spacing=8, controls=[
            primary_btn("Guardar", on_click=save_edit, color=C["green"]),
            primary_btn("Cancelar", on_click=cancel_edit, color=C["red"]),
        ]),
    ]

    def create_prod(_):
        try:
            register_product(
                f_cod.value, f_nom.value, f_pcom.value, f_pven.value,
                f_st.value, f_sm.value, f_cat.value, f_desc.value, actor,
            )
            show_snack(page, "Producto creado correctamente")
            for f in [f_cod, f_nom, f_pcom, f_pven, f_st, f_sm, f_cat, f_desc]:
                f.value = ""
            load_list()
        except ValueError as e:
            show_snack(page, str(e), False)

    f_search = field("Buscar por código o nombre…")
    f_search.on_submit = lambda _: load_list(f_search.value)

    body = [
        card(ft.Column(spacing=10, controls=[
            section_title("Nuevo Producto"),
            ft.Row(spacing=10, controls=[f_cod, f_nom]),
            ft.Row(spacing=10, controls=[f_pcom, f_pven, f_st, f_sm]),
            ft.Row(spacing=10, controls=[f_cat, f_desc]),
            primary_btn("Crear producto", on_click=create_prod),
        ])),
        card(ft.Column(spacing=10, controls=[
            section_title("Catálogo de Productos"),
            ft.Row(spacing=8, controls=[
                f_search,
                primary_btn("Buscar", on_click=lambda _: load_list(f_search.value)),
            ]),
            edit_form,
            ft.Divider(color=C["border"], thickness=1),
            results_col,
        ])),
    ]
    render_page(page, "productos", nav, user_data, body)
    load_list()
