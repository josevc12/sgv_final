import flet as ft

from app.services.user_service import (
    edit_user, get_all_users, register_user, toggle_user,
)
from app.views.shared import (
    C, card, field, pall, primary_btn, render_page, section_title,
    show_snack, status_chip,
)

ROLES = ["administrador", "cajero", "supervisor"]


def build_users_view(page, user_data, nav):
    actor = user_data["usuario"]

    f_nom  = field("Nombre completo*")
    f_usr  = field("Usuario*")
    f_pwd  = field("Contraseña*", password=True)
    dd_rol = ft.Dropdown(
        options=[ft.dropdown.Option(r, r.capitalize()) for r in ROLES],
        value="cajero",
        border_color=C["border"], focused_border_color=C["accent"],
        bgcolor=C["panel"], color=C["white"], text_size=13, height=44,
    )

    edit_form = ft.Column(spacing=8, visible=False)
    editing = {"id": None}

    f_e_nom = field("Nombre completo*")
    f_e_pwd = field("Nueva contraseña (opcional)", password=True)
    dd_e_rol = ft.Dropdown(
        options=[ft.dropdown.Option(r, r.capitalize()) for r in ROLES],
        value="cajero",
        border_color=C["border"], focused_border_color=C["accent"],
        bgcolor=C["panel"], color=C["white"], text_size=13, height=44,
    )

    users_col = ft.Column(spacing=6)

    def load_users():
        users_col.controls.clear()
        for u in get_all_users():
            active = u["estado"] == 1
            users_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(u["nombre"], size=13, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(f"@{u['usuario']}  |  Rol: {u['rol']}",
                                        size=11, color=C["lgrey"]),
                            ]),
                            ft.Row(spacing=6, controls=[
                                status_chip("Activo" if active else "Inactivo",
                                            C["green"] if active else C["grey"]),
                                ft.IconButton(
                                    ft.Icons.EDIT_OUTLINED,
                                    icon_size=18,
                                    icon_color=C["accent"],
                                    tooltip="Editar usuario",
                                    on_click=lambda _, u=u: open_edit(u),
                                ),
                                ft.IconButton(
                                    ft.Icons.TOGGLE_OFF if active
                                    else ft.Icons.TOGGLE_ON,
                                    icon_size=18,
                                    icon_color=C["red"] if active else C["green"],
                                    tooltip="Activar/Desactivar",
                                    on_click=lambda _, u=u: do_toggle(u),
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def create_user(_):
        try:
            register_user(f_nom.value, f_usr.value, f_pwd.value,
                          dd_rol.value, actor)
            show_snack(page, "Usuario creado correctamente")
            for f in [f_nom, f_usr, f_pwd]: f.value = ""
            load_users()
        except ValueError as e:
            show_snack(page, str(e), False)

    def do_toggle(u):
        toggle_user(u["id"], u["estado"], actor)
        load_users()

    def open_edit(u):
        editing["id"] = u["id"]
        f_e_nom.value = u["nombre"]
        dd_e_rol.value = u["rol"]
        f_e_pwd.value = ""
        edit_form.visible = True
        page.update()

    def save_edit(_):
        try:
            edit_user(editing["id"], f_e_nom.value, dd_e_rol.value,
                      f_e_pwd.value, actor)
            show_snack(page, "Usuario actualizado")
            edit_form.visible = False
            load_users()
        except ValueError as e:
            show_snack(page, str(e), False)

    def cancel_edit(_):
        edit_form.visible = False
        page.update()

    edit_form.controls = [
        section_title("Editar Usuario", 14),
        ft.Row(spacing=10, controls=[f_e_nom, dd_e_rol]),
        ft.Row(spacing=10, controls=[f_e_pwd]),
        ft.Row(spacing=8, controls=[
            primary_btn("Guardar", on_click=save_edit, color=C["green"]),
            primary_btn("Cancelar", on_click=cancel_edit, color=C["red"]),
        ]),
    ]

    body = [
        card(ft.Column(spacing=10, controls=[
            section_title("Nuevo Usuario"),
            ft.Row(spacing=10, controls=[f_nom, f_usr]),
            ft.Row(spacing=10, controls=[f_pwd, dd_rol]),
            primary_btn("Crear usuario", on_click=create_user),
        ])),
        card(ft.Column(spacing=10, controls=[
            section_title("Usuarios del Sistema"),
            ft.Divider(color=C["border"], thickness=1),
            edit_form,
            users_col,
        ])),
    ]
    render_page(page, "usuarios", nav, user_data, body)
    load_users()
