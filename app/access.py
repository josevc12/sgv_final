from typing import Set

ROLE_ACCESS = {
    "administrador": {
        "dashboard",
        "productos",
        "clientes",
        "inventario",
        "pos",
        "facturas",
        "caja",
        "reportes",
        "usuarios",
    },
    "cajero": {
        "dashboard",
        "pos",
        "facturas",
        "caja",
        "clientes",
    },
    "supervisor": {
        "dashboard",
        "inventario",
        "reportes",
        "facturas",
    },
}


def allowed_views(role: str) -> Set[str]:
    return ROLE_ACCESS.get(role, set())


def can_access(role: str, view_key: str) -> bool:
    return view_key in allowed_views(role)
