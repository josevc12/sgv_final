import flet as ft

from app.config import APP_TITLE, BG_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH
from app.db.init_db import initialize_database
from app.router import AppRouter


def main(page: ft.Page):
    page.title          = APP_TITLE
    page.window.width   = WINDOW_WIDTH
    page.window.height  = WINDOW_HEIGHT
    page.window.resizable = True
    page.bgcolor        = BG_COLOR
    page.padding        = 0

    initialize_database()

    router = AppRouter(page)
    router.start()


def run_app():
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
