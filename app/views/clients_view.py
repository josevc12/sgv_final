import flet as ft

from app.services.client_service import (
    edit_client, get_all_clients, get_purchase_history, register_client,
)
from app.views.shared import (
    C, card, field, pall, primary_btn, render_page, section_title,
    show_snack, status_chip,
)


def build_clients_view(page, user_data, nav):
    actor = user_data["usuario"]

    f_nom   = field("Nombre*")
    f_doc   = field("Documento*")
    f_tel   = field("Teléfono")
    f_email = field("Email")
    f_dir   = field("Dirección")
    f_search = field("Buscar cliente…")

    edit_form   = ft.Column(spacing=8, visible=False)
    editing     = {"id": None}

    f_e_nom   = field("Nombre*")
    f_e_doc   = field("Documento*")
    f_e_tel   = field("Teléfono")
    f_e_email = field("Email")
    f_e_dir   = field("Dirección")

    results_col  = ft.Column(spacing=6)
    history_col  = ft.Column(spacing=4)
    history_title = ft.Text("", size=14, color=C["text"], weight=ft.FontWeight.W_700)

    def load_list(q=""):
        results_col.controls.clear()
        clients = get_all_clients(q)
        if not clients:
            results_col.controls.append(ft.Text("Sin resultados.", color=C["grey"]))
        for cl in clients:
            results_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(cl["nombre"], size=13, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Doc: {cl['documento']}  |  "
                                    f"Tel: {cl['telefono'] or '—'}  |  "
                                    f"{cl['email'] or '—'}",
                                    size=11, color=C["lgrey"],
                                ),
                            ]),
                            ft.Row(spacing=6, controls=[
                                ft.IconButton(
                                    ft.Icons.EDIT_OUTLINED, icon_size=18,
                                    icon_color=C["accent"],
                                    tooltip="Editar cliente",
                                    on_click=lambda _, cl=cl: open_edit(cl),
                                ),
                                ft.IconButton(
                                    ft.Icons.HISTORY, icon_size=18,
                                    icon_color=C["accent"],
                                    tooltip="Ver historial",
                                    on_click=lambda _, cl=cl: show_history(cl),
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def open_edit(cl):
        editing["id"] = cl["id"]
        f_e_nom.value   = cl["nombre"]
        f_e_doc.value   = cl["documento"]
        f_e_tel.value   = cl["telefono"]
        f_e_email.value = cl["email"]
        f_e_dir.value   = cl["direccion"]
        edit_form.visible = True
        page.update()

    def save_edit(_):
        try:
            edit_client(
                editing["id"], f_e_nom.value, f_e_doc.value,
                f_e_tel.value, f_e_email.value, f_e_dir.value, actor,
            )
            show_snack(page, "Cliente actualizado")
            edit_form.visible = False
            load_list(f_search.value)
        except ValueError as e:
            show_snack(page, str(e), False)

    def cancel_edit(_):
        edit_form.visible = False
        page.update()

    def show_history(cl):
        history_col.controls.clear()
        history_title.value = f"Historial de compras – {cl['nombre']}"
        rows = get_purchase_history(cl["id"])
        if not rows:
            history_col.controls.append(
                ft.Text("Sin compras registradas.", color=C["grey"]))
        for r in rows:
            history_col.controls.append(
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text(r[1][:16], size=12, color=C["lgrey"]),
                    ft.Text(f"${r[2]:.2f}", size=12, color=C["green"],
                            weight=ft.FontWeight.W_600),
                    status_chip(r[3], C["header"]),
                ])
            )
        page.update()

    def create_cl(_):
        try:
            register_client(f_nom.value, f_doc.value,
                            f_tel.value, f_email.value, f_dir.value, actor)
            show_snack(page, "Cliente registrado correctamente")
            for f in [f_nom, f_doc, f_tel, f_email, f_dir]:
                f.value = ""
            load_list()
        except ValueError as e:
            show_snack(page, str(e), False)

    f_search.on_submit = lambda _: load_list(f_search.value)

    edit_form.controls = [
        section_title("Editar cliente", 14),
        ft.Row(spacing=10, controls=[f_e_nom, f_e_doc]),
        ft.Row(spacing=10, controls=[f_e_tel, f_e_email, f_e_dir]),
        ft.Row(spacing=8, controls=[
            primary_btn("Guardar", on_click=save_edit, color=C["green"]),
            primary_btn("Cancelar", on_click=cancel_edit, color=C["red"]),
        ]),
    ]

    body = [
        card(ft.Column(spacing=10, controls=[
            section_title("Nuevo Cliente"),
            ft.Row(spacing=10, controls=[f_nom, f_doc]),
            ft.Row(spacing=10, controls=[f_tel, f_email, f_dir]),
            primary_btn("Registrar cliente", on_click=create_cl),
        ])),
        card(ft.Column(spacing=10, controls=[
            section_title("Clientes Registrados"),
            ft.Row(spacing=8, controls=[
                f_search,
                primary_btn("Buscar", on_click=lambda _: load_list(f_search.value)),
            ]),
            edit_form,
            ft.Divider(color=C["border"], thickness=1),
            results_col,
            ft.Container(height=6),
            history_title,
            history_col,
        ])),
    ]
    render_page(page, "clientes", nav, user_data, body)
    load_list()
