import flet as ft

from app.services.auth_service import (
    get_login_preferences, save_login_preferences, verify_credentials,
)
from app.views.shared import C, br_only, pall, psym


def build_login_view(page, on_login_success):
    page.clean()
    page.bgcolor = C["bg"]

    prefs = get_login_preferences()

    f_user = ft.TextField(
        hint_text="Usuario", value=prefs["username"],
        border_color=C["border"], focused_border_color=C["accent"],
        border_radius=10, bgcolor=C["panel"], color=C["white"],
        hint_style=ft.TextStyle(color="#3A4A6A"), text_size=13, height=44,
        content_padding=psym(12, 10),
    )
    f_pass = ft.TextField(
        hint_text="Contraseña", password=True, can_reveal_password=True,
        border_color=C["border"], focused_border_color=C["accent"],
        border_radius=10, bgcolor=C["panel"], color=C["white"],
        hint_style=ft.TextStyle(color="#3A4A6A"), text_size=13, height=44,
        content_padding=psym(12, 10),
    )
    f_rem = ft.Checkbox(
        label="Recordar sesión", value=prefs["remember"],
        fill_color=C["accent"], check_color=C["white"],
        label_style=ft.TextStyle(color=C["grey"], size=12),
    )
    err  = ft.Text("", color="#E05A5A", size=12, visible=False)
    ring = ft.ProgressRing(width=20, height=20, stroke_width=2,
                           color=C["accent"], visible=False)

    def do_login(_):
        usr = f_user.value.strip()
        pwd = f_pass.value
        err.visible = False
        if not usr or not pwd:
            err.value = "Completa todos los campos"
            err.visible = True
            page.update()
            return
        ring.visible = True
        page.update()
        user = verify_credentials(usr, pwd)
        if user:
            save_login_preferences(usr, f_rem.value)
            on_login_success(user)
            return
        err.value = "Usuario o contraseña incorrectos"
        err.visible = True
        ring.visible = False
        page.update()

    f_pass.on_submit = do_login
    f_user.on_submit = lambda _: f_pass.focus()

    left = ft.Container(
        width=310, bgcolor=C["sidebar"],
        border_radius=br_only(tl=20, bl=20), padding=pall(44),
        content=ft.Column(expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(spacing=8, controls=[
                    ft.Container(
                        width=52, height=52, border_radius=12, bgcolor="#1A2E50",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("SGV", size=17, weight=ft.FontWeight.W_800,
                                        color=C["accent"]),
                    ),
                    ft.Container(height=24),
                    ft.Text("Sistema de\nGestión de\nVentas", size=26,
                            weight=ft.FontWeight.W_800, color=C["white"]),
                    ft.Container(height=8),
                    ft.Text("Centraliza. Controla. Crece.",
                            size=12, color=C["accent"], italic=True),
                ]),
                ft.Text("v1.0.0 – Completo", size=10, color=C["border"]),
            ],
        ),
    )

    right = ft.Container(
        expand=True, bgcolor=C["card"],
        border_radius=br_only(tr=20, br_=20), padding=psym(48, 44),
        content=ft.Column(expand=True,
            alignment=ft.MainAxisAlignment.CENTER, spacing=0,
            controls=[
                ft.Text("Iniciar Sesión", size=22, weight=ft.FontWeight.W_700,
                        color=C["white"]),
                ft.Container(height=4),
                ft.Text("Ingresa tus credenciales para continuar",
                        size=12, color=C["grey"]),
                ft.Container(height=28),
                ft.Text("Usuario", size=11, color=C["grey"], weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                f_user,
                ft.Container(height=12),
                ft.Text("Contraseña", size=11, color=C["grey"], weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                f_pass,
                ft.Container(height=8),
                f_rem,
                err,
                ft.Container(height=8),
                ft.Row([ring], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    height=44, border_radius=8, bgcolor=C["accent"],
                    on_click=do_login,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("INGRESAR", color=C["white"], size=13,
                                    weight=ft.FontWeight.W_700),
                ),
            ],
        ),
    )

    page.add(
        ft.Container(expand=True, bgcolor=C["bg"],
            alignment=ft.Alignment(0, 0),
            content=ft.Container(
                width=740, height=490, border_radius=20,
                shadow=ft.BoxShadow(blur_radius=50,
                                    color=ft.Colors.with_opacity(0.4, "#000000"),
                                    offset=ft.Offset(0, 16)),
                content=ft.Row(spacing=0, expand=True, controls=[left, right]),
            ),
        )
    )
    page.update()
