import os
import flet as ft

from app.repositories.invoices_repository import get_invoice_info, list_invoices
from app.services.invoice_service import annul_invoice
from app.services.sales_service import get_items_for_sale
from app.views.shared import (
    C, card, pall, render_page, section_title, show_snack, status_chip,
)

# Carpeta donde se guardarán los PDFs generados
PDF_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "SGV_Facturas")


def _generate_invoice_pdf(info: dict, items: list) -> str:
    """
    Genera un PDF de la factura y lo guarda en ~/SGV_Facturas/.

    Args:
        info:  Diccionario con los datos de la factura (get_invoice_info).
        items: Lista de ítems de la venta (get_items_for_sale).

    Returns:
        Ruta absoluta del archivo PDF generado.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )

    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

    # Nombre del archivo basado en el número de factura (sin caracteres especiales)
    safe_name = info["numero"].replace("/", "-").replace("\\", "-")
    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"{safe_name}.pdf")

    # ── Estilos ──────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    AZUL   = colors.HexColor("#2D3F8F")
    OSCURO = colors.HexColor("#080E1A")
    GRIS   = colors.HexColor("#7F91A3")
    VERDE  = colors.HexColor("#2E8F43")
    BLANCO = colors.white

    titulo_style = ParagraphStyle(
        "titulo", fontName="Helvetica-Bold", fontSize=22,
        textColor=BLANCO, alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "sub", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER,
    )
    label_style = ParagraphStyle(
        "label", fontName="Helvetica-Bold", fontSize=9,
        textColor=GRIS,
    )
    valor_style = ParagraphStyle(
        "valor", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#DCE5FF"),
    )
    total_style = ParagraphStyle(
        "total", fontName="Helvetica-Bold", fontSize=14,
        textColor=VERDE, alignment=TA_RIGHT,
    )
    footer_style = ParagraphStyle(
        "footer", fontName="Helvetica", fontSize=8,
        textColor=GRIS, alignment=TA_CENTER,
    )

    story = []

    # ── Encabezado ────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("SGV", titulo_style),
        Paragraph(f"FACTURA<br/>{info['numero']}", sub_style),
    ]]
    header_table = Table(header_data, colWidths=[9*cm, 8.5*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), OSCURO),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # ── Datos de la factura ───────────────────────────────────────────────
    fecha_fmt = info["fecha"][:16] if info.get("fecha") else ""
    info_data = [
        [Paragraph("Fecha:", label_style),        Paragraph(fecha_fmt, valor_style),
         Paragraph("Estado:", label_style),        Paragraph(info["estado"].capitalize(), valor_style)],
        [Paragraph("Cliente:", label_style),       Paragraph(info["cliente"], valor_style),
         Paragraph("Método de pago:", label_style), Paragraph(info["metodo_pago"].capitalize(), valor_style)],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 3.5*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0F1624")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#2A3A5C")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#1A2A4A")),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ── Tabla de productos ────────────────────────────────────────────────
    col_header = ParagraphStyle("ch", fontName="Helvetica-Bold", fontSize=9, textColor=BLANCO)
    col_body   = ParagraphStyle("cb", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#DCE5FF"))
    col_right  = ParagraphStyle("cr", fontName="Helvetica", fontSize=9, textColor=VERDE, alignment=TA_RIGHT)

    prod_data = [[
        Paragraph("Producto",   col_header),
        Paragraph("Cant.",      col_header),
        Paragraph("Precio/u",   col_header),
        Paragraph("Subtotal",   col_header),
    ]]
    for it in items:
        prod_data.append([
            Paragraph(it["nombre"],          col_body),
            Paragraph(str(it["cantidad"]),   col_body),
            Paragraph(f"${it['precio']:.2f}", col_body),
            Paragraph(f"${it['subtotal']:.2f}", col_right),
        ])

    prod_table = Table(prod_data, colWidths=[10*cm, 2*cm, 3*cm, 2.5*cm])
    prod_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1),
         [colors.HexColor("#0F1624"), colors.HexColor("#111B2E")]),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#2A3A5C")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#1A2A4A")),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (3, 0), (3, -1), "RIGHT"),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 12))

    # ── Totales ───────────────────────────────────────────────────────────
    totales_data = [
        ["", Paragraph("Subtotal:", label_style),  Paragraph(f"${info['subtotal']:.2f}", col_right)],
        ["", Paragraph("IVA (19%):", label_style), Paragraph(f"${info['impuestos']:.2f}", col_right)],
        ["", Paragraph("TOTAL:",     ParagraphStyle("tb", fontName="Helvetica-Bold", fontSize=13, textColor=VERDE)),
             Paragraph(f"${info['total']:.2f}", ParagraphStyle("tv", fontName="Helvetica-Bold", fontSize=13, textColor=VERDE, alignment=TA_RIGHT))],
    ]
    totales_table = Table(totales_data, colWidths=[9.5*cm, 4*cm, 4*cm])
    totales_table.setStyle(TableStyle([
        ("BACKGROUND",    (1, 0), (-1, -1), colors.HexColor("#0F1624")),
        ("BOX",           (1, 0), (-1, -1), 0.5, colors.HexColor("#2A3A5C")),
        ("LINEABOVE",     (1, 2), (-1, 2), 1, VERDE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (1, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (1, 0), (-1, -1), 10),
    ]))
    story.append(totales_table)
    story.append(Spacer(1, 30))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=colors.HexColor("#2A3A5C"), spaceAfter=8))
    story.append(Paragraph(
        "SGV – Sistema de Gestión de Ventas  ·  Documento generado automáticamente",
        footer_style,
    ))

    # ── Construir PDF ─────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=f"Factura {info['numero']}",
        author="SGV",
    )
    doc.build(story)
    return pdf_path


def build_invoices_view(page, user_data, nav):
    actor = user_data["usuario"]
    invoices_col = ft.Column(spacing=6)
    detail_col   = ft.Column(spacing=4)
    detail_title = ft.Text("", size=14, color=C["text"], weight=ft.FontWeight.W_700)

    def load_invoices():
        invoices_col.controls.clear()
        invoices = list_invoices(30)
        if not invoices:
            invoices_col.controls.append(
                ft.Text("No hay facturas registradas.", color=C["grey"]))
        for inv in invoices:
            status_color = C["green"] if inv["estado"] == "activa" else C["grey"]
            invoices_col.controls.append(
                ft.Container(
                    bgcolor=C["panel"], border_radius=8, padding=pall(10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, expand=True, controls=[
                                ft.Text(f"{inv['numero']}",
                                        size=13, color=C["text"],
                                        weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Cliente: {inv['cliente']}  |  "
                                    f"Fecha: {inv['fecha'][:16]}",
                                    size=11, color=C["lgrey"],
                                ),
                            ]),
                            ft.Row(spacing=8, controls=[
                                status_chip(inv["estado"].capitalize(), status_color),
                                ft.Text(f"${inv['total']:.2f}",
                                        size=14, color=C["green"],
                                        weight=ft.FontWeight.W_700),
                                ft.IconButton(
                                    ft.Icons.RECEIPT_LONG_OUTLINED,
                                    icon_size=18, icon_color=C["accent"],
                                    tooltip="Ver detalle",
                                    on_click=lambda _, inv=inv: show_detail(inv),
                                ),
                                ft.IconButton(
                                    ft.Icons.PICTURE_AS_PDF_OUTLINED,
                                    icon_size=18, icon_color=C["accent"],
                                    tooltip="Generar PDF",
                                    on_click=lambda _, inv=inv: do_print(inv),
                                ),
                                ft.IconButton(
                                    ft.Icons.CANCEL_OUTLINED,
                                    icon_size=18, icon_color=C["red"],
                                    tooltip="Anular factura",
                                    disabled=inv["estado"] != "activa",
                                    on_click=lambda _, inv=inv: do_annul(inv),
                                ),
                            ]),
                        ],
                    ),
                )
            )
        page.update()

    def do_print(inv):
        """Genera un PDF real de la factura y notifica la ruta al usuario."""
        info = get_invoice_info(inv["id"])
        if not info:
            show_snack(page, "Factura no encontrada", False)
            return
        items = get_items_for_sale(info["id_venta"])
        try:
            pdf_path = _generate_invoice_pdf(info, items)
            show_snack(page, f"PDF guardado en: {pdf_path}")
        except Exception as e:
            show_snack(page, f"Error al generar PDF: {e}", False)

    def do_annul(inv):
        try:
            info = annul_invoice(inv["id"], actor)
            show_snack(page, f"Factura {info['numero']} anulada")
            load_invoices()
            detail_col.controls.clear()
            detail_title.value = ""
            page.update()
        except ValueError as e:
            show_snack(page, str(e), False)

    def show_detail(inv):
        detail_col.controls.clear()
        detail_title.value = f"Detalle – {inv['numero']}"
        info = get_invoice_info(inv["id"])
        if not info:
            detail_col.controls.append(
                ft.Text("Factura no encontrada.", color=C["grey"]))
            page.update()
            return

        items = get_items_for_sale(info["id_venta"])

        if not items:
            detail_col.controls.append(
                ft.Text("Sin detalle disponible.", color=C["grey"]))
        else:
            detail_col.controls.append(
                ft.Row(controls=[
                    ft.Text("Producto", size=11, color=C["grey"], expand=True),
                    ft.Text("Cant.",    size=11, color=C["grey"]),
                    ft.Text("P/U",      size=11, color=C["grey"]),
                    ft.Text("Subtotal", size=11, color=C["grey"]),
                ])
            )
            detail_col.controls.append(
                ft.Divider(color=C["border"], thickness=1))
            for it in items:
                detail_col.controls.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(it["nombre"], size=12,
                                    color=C["text"], expand=True),
                            ft.Text(str(it["cantidad"]), size=12, color=C["lgrey"]),
                            ft.Text(f"${it['precio']:.2f}", size=12, color=C["lgrey"]),
                            ft.Text(f"${it['subtotal']:.2f}", size=12,
                                    color=C["green"],
                                    weight=ft.FontWeight.W_600),
                        ],
                    )
                )
            detail_col.controls.append(ft.Divider(color=C["border"], thickness=1))
            detail_col.controls.append(
                ft.Row(alignment=ft.MainAxisAlignment.END, controls=[
                    ft.Text(f"Total:  ${info['total']:.2f}",
                            size=14, color=C["green"],
                            weight=ft.FontWeight.W_700),
                ])
            )
        page.update()

    body = [
        card(ft.Column(spacing=10, controls=[
            section_title("Facturas Generadas"),
            ft.Divider(color=C["border"], thickness=1),
            invoices_col,
        ])),
        card(ft.Column(spacing=8, controls=[
            detail_title,
            detail_col,
        ])),
    ]
    render_page(page, "facturas", nav, user_data, body)
    load_invoices()