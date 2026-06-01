import flet as ft

from app.access import allowed_views

# ── Paleta de colores ──────────────────────────────────────────────────────────
C = {
    "bg":      "#080E1A",
    "sidebar": "#0D1526",
    "card":    "#0F1624",
    "panel":   "#111B2E",
    "border":  "#2A3A5C",
    "accent":  "#4A90D9",
    "header":  "#2D3F8F",
    "white":   "#FFFFFF",
    "grey":    "#7F91A3",
    "lgrey":   "#A5B5C5",
    "text":    "#DCE5FF",
    "green":   "#2E8F43",
    "red":     "#C0392B",
    "orange":  "#D97A00",
    "yellow":  "#F2A24B",
}

_NAV_LABELS = {
    "dashboard":  "Dashboard",
    "productos":  "Productos",
    "clientes":   "Clientes",
    "inventario": "Inventario",
    "pos":        "Punto de Venta",
    "facturas":   "Facturas",
    "caja":       "Caja",
    "reportes":   "Reportes",
    "usuarios":   "Usuarios",
}

# ── Helpers de padding / border-radius ────────────────────────────────────────

def psym(h, v):
    try:    return ft.Padding.symmetric(horizontal=h, vertical=v)
    except: return ft.padding.symmetric(horizontal=h, vertical=v)


def pall(n):
    try:    return ft.Padding.all(n)
    except: return ft.padding.all(n)


def br_only(tl=0, tr=0, bl=0, br_=0):
    try:    return ft.BorderRadius.only(top_left=tl, top_right=tr,
                                        bottom_left=bl, bottom_right=br_)
    except: return ft.border_radius.only(top_left=tl, top_right=tr,
                                         bottom_left=bl, bottom_right=br_)


def viewport_width(page):
    w = getattr(page, "width", None)
    if isinstance(w, (int, float)) and w > 0:
        return w
    win = getattr(page, "window", None)
    if win:
        ww = getattr(win, "width", None)
        if isinstance(ww, (int, float)) and ww > 0:
            return ww
    return 1280

# ── Componentes reutilizables ─────────────────────────────────────────────────

def field(hint, value="", password=False, expand=False, width=None):
    kw = dict(
        hint_text=hint, value=str(value), password=password,
        can_reveal_password=password,
        border_color=C["border"], focused_border_color=C["accent"],
        border_radius=10, bgcolor=C["panel"], color=C["white"],
        hint_style=ft.TextStyle(color="#3A4A6A"),
        text_size=13, height=44,
        content_padding=psym(12, 10),
    )
    if expand: kw["expand"] = True
    if width:  kw["width"]  = width
    return ft.TextField(**kw)


def primary_btn(text, on_click=None, color=None, expand=False):
    return ft.Container(
        expand=expand,
        height=44,
        border_radius=8,
        bgcolor=color or C["accent"],
        on_click=on_click,
        padding=psym(16, 0),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(text, color=C["white"], size=13, weight=ft.FontWeight.W_600),
    )


def card(content, padding=14):
    return ft.Container(
        bgcolor=C["card"], border_radius=12,
        border=ft.border.all(1, C["border"]),
        padding=pall(padding), content=content,
    )


def section_title(text, size=18):
    return ft.Text(text, size=size, color=C["text"], weight=ft.FontWeight.W_700)


def small_label(text):
    return ft.Text(text, size=11, color=C["grey"], weight=ft.FontWeight.W_600)


def status_chip(text, color):
    return ft.Container(
        border_radius=7, bgcolor=color,
        padding=psym(10, 3),
        content=ft.Text(text, size=11, color=C["white"], weight=ft.FontWeight.W_700),
    )


def show_snack(page, message, success=True):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=C["green"] if success else C["red"],
    )
    page.snack_bar.open = True
    page.update()

# ── Sidebar ───────────────────────────────────────────────────────────────────

def _menu_item(label, active=False, on_tap=None):
    return ft.Container(
        height=40, border_radius=8,
        bgcolor=C["header"] if active else "transparent",
        padding=psym(12, 0),
        on_click=(lambda _: on_tap()) if on_tap else None,
        content=ft.Row(spacing=10, controls=[
            ft.Container(width=6, height=6, border_radius=3,
                         bgcolor=C["white"] if active else C["grey"]),
            ft.Text(label, size=13,
                    color=C["white"] if active else C["lgrey"],
                    weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400),
        ]),
    )


def build_sidebar(active_key, nav, on_logout, user_data, compact=False):
    width = 170 if compact else 210
    role = (user_data or {}).get("rol", "")
    allowed = allowed_views(role)
    items = [kv for kv in _NAV_LABELS.items() if kv[0] in allowed]

    menu = [
        ft.Container(padding=psym(8, 14), content=ft.Column(spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Text("SGV", size=28, weight=ft.FontWeight.W_800, color=C["text"]),
                ft.Text("Sistema de Ventas", size=10, color=C["grey"]),
            ])),
        ft.Divider(color=C["border"], thickness=1),
    ]
    for key, lbl in items:
        menu.append(_menu_item(lbl, active=(active_key == key),
                               on_tap=nav.get(key)))

    menu += [
        ft.Container(expand=True),
        ft.Divider(color=C["border"], thickness=1),
        ft.Container(
            height=38, border_radius=8, bgcolor="#1A2A3A", padding=psym(12, 0),
            on_click=lambda _: on_logout(),
            content=ft.Row(spacing=8, controls=[
                ft.Icon(ft.Icons.LOGOUT, size=16, color=C["lgrey"]),
                ft.Text("Cerrar sesión", size=13, color=C["lgrey"]),
            ]),
        ),
    ]
    return ft.Container(
        width=width, bgcolor=C["sidebar"], padding=pall(10),
        content=ft.Column(spacing=4, expand=True, controls=menu),
    )

# ── Top bar ───────────────────────────────────────────────────────────────────

def build_topbar(active_key, user_data):
    title = _NAV_LABELS.get(active_key, active_key.capitalize())
    return ft.Container(
        height=54, bgcolor=C["header"], padding=psym(20, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(title, size=19, color=C["white"], weight=ft.FontWeight.W_700),
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=C["text"]),
                    ft.Text(
                        f"{user_data['nombre']}  ·  {user_data['rol'].capitalize()}",
                        size=13, color=C["text"],
                    ),
                ]),
            ],
        ),
    )

# ── Shell principal ───────────────────────────────────────────────────────────

def render_page(page, active_key, nav, user_data, body_controls):
    """Limpia la página y construye sidebar + topbar + cuerpo scrolleable."""
    page.clean()
    page.bgcolor = C["bg"]
    compact = viewport_width(page) < 1100
    sb = build_sidebar(active_key, nav, nav["logout"], user_data, compact=compact)
    tb = build_topbar(active_key, user_data)

    page.add(
        ft.Row(spacing=0, expand=True, controls=[
            sb,
            ft.Column(spacing=0, expand=True, controls=[
                tb,
                ft.Container(
                    expand=True, bgcolor=C["bg"], padding=pall(16),
                    content=ft.Column(
                        spacing=14, expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=body_controls,
                    ),
                ),
            ]),
        ])
    )
    page.update()
