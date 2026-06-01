from app.access import can_access
from app.views.caja_view import build_caja_view
from app.views.clients_view import build_clients_view
from app.views.dashboard_view import build_dashboard_view
from app.views.inventory_view import build_inventory_view
from app.views.invoices_view import build_invoices_view
from app.views.login_view import build_login_view
from app.views.pos_view import build_pos_view
from app.views.products_view import build_products_view
from app.views.reports_view import build_reports_view
from app.views.users_view import build_users_view


class AppRouter:
    def __init__(self, page):
        self.page         = page
        self.current_user = None
        self.current_view = "login"
        self.page.on_resized = self._on_resized

    def start(self):
        self.show_login()

    # ── vistas ────────────────────────────────────────────────────────────────

    def show_login(self):
        self.current_view = "login"
        build_login_view(self.page, on_login_success=self._on_login)

    def show_dashboard(self):
        self.current_view = "dashboard"
        build_dashboard_view(self.page, self.current_user, self._nav())

    def show_productos(self):
        if not self._ensure_access("productos"):
            return
        self.current_view = "productos"
        build_products_view(self.page, self.current_user, self._nav())

    def show_clientes(self):
        if not self._ensure_access("clientes"):
            return
        self.current_view = "clientes"
        build_clients_view(self.page, self.current_user, self._nav())

    def show_inventario(self):
        if not self._ensure_access("inventario"):
            return
        self.current_view = "inventario"
        build_inventory_view(self.page, self.current_user, self._nav())

    def show_pos(self):
        if not self._ensure_access("pos"):
            return
        self.current_view = "pos"
        build_pos_view(self.page, self.current_user, self._nav())

    def show_facturas(self):
        if not self._ensure_access("facturas"):
            return
        self.current_view = "facturas"
        build_invoices_view(self.page, self.current_user, self._nav())

    def show_caja(self):
        if not self._ensure_access("caja"):
            return
        self.current_view = "caja"
        build_caja_view(self.page, self.current_user, self._nav())

    def show_reportes(self):
        if not self._ensure_access("reportes"):
            return
        self.current_view = "reportes"
        build_reports_view(self.page, self.current_user, self._nav())

    def show_usuarios(self):
        if not self._ensure_access("usuarios"):
            return
        self.current_view = "usuarios"
        build_users_view(self.page, self.current_user, self._nav())

    def logout(self):
        self.current_user = None
        self.show_login()

    def _ensure_access(self, view_key):
        if not self.current_user:
            self.show_login()
            return False
        if not can_access(self.current_user["rol"], view_key):
            self.show_dashboard()
            return False
        return True

    # ── helpers ───────────────────────────────────────────────────────────────

    def _on_login(self, user_data):
        self.current_user = user_data
        self.show_dashboard()

    def _nav(self):
        return {
            "dashboard":  self.show_dashboard,
            "productos":  self.show_productos,
            "clientes":   self.show_clientes,
            "inventario": self.show_inventario,
            "pos":        self.show_pos,
            "facturas":   self.show_facturas,
            "caja":       self.show_caja,
            "reportes":   self.show_reportes,
            "usuarios":   self.show_usuarios,
            "logout":     self.logout,
        }

    def _on_resized(self, _):
        view_map = {
            "dashboard":  self.show_dashboard,
            "productos":  self.show_productos,
            "clientes":   self.show_clientes,
            "inventario": self.show_inventario,
            "pos":        self.show_pos,
            "facturas":   self.show_facturas,
            "caja":       self.show_caja,
            "reportes":   self.show_reportes,
            "usuarios":   self.show_usuarios,
        }
        if self.current_view in view_map and self.current_user:
            view_map[self.current_view]()
