from app.repositories.audit_repository import log_event
from app.repositories.invoices_repository import get_invoice_info, set_invoice_state
from app.repositories.sales_repository import set_sale_state


def annul_invoice(invoice_id, actor=""):
    info = get_invoice_info(invoice_id)
    if not info:
        raise ValueError("Factura no encontrada")
    if info["estado"] == "anulada":
        raise ValueError("La factura ya está anulada")
    set_invoice_state(invoice_id, "anulada")
    set_sale_state(info["id_venta"], "anulada")
    log_event("factura_anulada", actor, f"Anuló {info['numero']}")
    return info
