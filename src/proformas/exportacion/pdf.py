"""Generación de proformas en PDF con ReportLab."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from proformas.dominio import Proforma


class ExportadorProformaPDF:
    """Crea un documento comercial legible a partir de una proforma guardada."""

    def __init__(
        self,
        empresa: str = "CM INSUMOS MEDICOS",
        ruc_empresa: str = "1150755997-001",
        telefono_empresa: str = "0997594324",
    ) -> None:
        self.empresa = empresa
        self.ruc_empresa = ruc_empresa
        self.telefono_empresa = telefono_empresa

    def exportar(self, proforma: Proforma, destino: str | Path) -> Path:
        ruta = Path(destino)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        estilos = getSampleStyleSheet()
        fuente_regular, fuente_negrita = self._registrar_fuentes()
        for estilo in estilos.byName.values():
            estilo.fontName = fuente_regular
        estilos["Title"].fontName = fuente_negrita
        normal = estilos["BodyText"]
        pequeno = ParagraphStyle("Pequeno", parent=normal, fontSize=8, leading=10)
        derecha = ParagraphStyle("Derecha", parent=normal, alignment=TA_RIGHT)
        documento = SimpleDocTemplate(
            str(ruta),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=f"Proforma {proforma.numero}",
            author=self.empresa,
        )

        contenido = [
            Table(
                [
                    [
                        Paragraph(f"<b>{self.empresa}</b>", estilos["Title"]),
                        Paragraph(f"<b>PROFORMA</b><br/>{proforma.numero}", derecha),
                    ]
                ],
                colWidths=[120 * mm, 54 * mm],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LINEBELOW", (0, 0), (-1, -1), 2, colors.HexColor("#1D4ED8")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ]
                ),
            ),
            Spacer(1, 5 * mm),
            Table(
                [
                    [
                        Paragraph(f"<b>RUC:</b> {self.ruc_empresa}", normal),
                        Paragraph(f"<b>Telefono:</b> {self.telefono_empresa}", normal),
                        Paragraph(f"<b>Fecha:</b> {proforma.fecha:%d/%m/%Y}", normal),
                    ],
                    [Paragraph(f"<b>Cliente:</b> {proforma.cliente.nombre}", normal), "", ""],
                    [
                        Paragraph(
                            f"<b>Identificacion:</b> {proforma.cliente.identificacion}", normal
                        ),
                        Paragraph(f"<b>Telefono:</b> {proforma.cliente.telefono or '-'}", normal),
                        "",
                    ],
                    [
                        Paragraph(f"<b>Direccion:</b> {proforma.cliente.direccion or '-'}", normal),
                        "",
                        "",
                    ],
                ],
                colWidths=[92 * mm, 48 * mm, 34 * mm],
                style=TableStyle(
                    [
                        ("SPAN", (0, 1), (2, 1)),
                        ("SPAN", (1, 2), (2, 2)),
                        ("SPAN", (0, 3), (2, 3)),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6FA")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFD8E6")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DCE3ED")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            ),
            Spacer(1, 5 * mm),
        ]

        filas = [["Cant.", "Codigo", "Descripcion", "Precio U.", "Desc.", "IVA", "Total"]]
        filas.extend(
            [
                str(item.cantidad),
                item.producto.codigo,
                Paragraph(
                    f"{item.producto.nombre}{f' - Talla {item.talla.value}' if item.talla else ''}",
                    pequeno,
                ),
                f"${float(item.producto.precio):,.2f}",
                f"{item.descuento_pct:.0f}%",
                f"{item.producto.iva_pct:.0f}%",
                f"${item.total():,.2f}",
            ]
            for item in proforma.items
        )
        contenido.append(
            Table(
                filas,
                repeatRows=1,
                colWidths=[14 * mm, 24 * mm, 59 * mm, 22 * mm, 16 * mm, 14 * mm, 25 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173A6B")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), fuente_negrita),
                        ("ALIGN", (0, 0), (1, -1), "CENTER"),
                        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CFD8E6")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#F8FAFC")],
                        ),
                        ("PADDING", (0, 0), (-1, -1), 5),
                    ]
                ),
            )
        )
        contenido.extend(
            [
                Spacer(1, 5 * mm),
                Table(
                    [
                        ["Subtotal", f"${proforma.subtotal():,.2f}"],
                        ["IVA", f"${proforma.impuesto():,.2f}"],
                        [
                            Paragraph("<b>TOTAL</b>", normal),
                            Paragraph(f"<b>${proforma.total():,.2f}</b>", derecha),
                        ],
                    ],
                    colWidths=[35 * mm, 32 * mm],
                    hAlign="RIGHT",
                    style=TableStyle(
                        [
                            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                            ("LINEABOVE", (0, -1), (-1, -1), 1.2, colors.HexColor("#173A6B")),
                            ("PADDING", (0, 0), (-1, -1), 5),
                        ]
                    ),
                ),
                Spacer(1, 6 * mm),
                Paragraph(f"<b>Observaciones</b><br/>{proforma.observaciones or '-'}", normal),
                Spacer(1, 3 * mm),
                Paragraph(
                    f"<b>Instrucciones de pago</b><br/>{proforma.instrucciones_pago or '-'}",
                    normal,
                ),
                Spacer(1, 8 * mm),
                Paragraph("Precios sujetos a impuestos indicados en cada producto.", pequeno),
            ]
        )
        documento.build(contenido)
        return ruta

    @staticmethod
    def _registrar_fuentes() -> tuple[str, str]:
        """Usa Liberation Sans cuando está disponible y conserva un fallback portable."""
        directorio = Path("/usr/share/fonts/liberation-sans-fonts")
        regular = directorio / "LiberationSans-Regular.ttf"
        negrita = directorio / "LiberationSans-Bold.ttf"
        if not regular.exists() or not negrita.exists():
            return "Helvetica", "Helvetica-Bold"
        if "CM-Regular" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("CM-Regular", regular))
            pdfmetrics.registerFont(TTFont("CM-Bold", negrita))
            pdfmetrics.registerFontFamily(
                "CM-Regular",
                normal="CM-Regular",
                bold="CM-Bold",
                italic="CM-Regular",
                boldItalic="CM-Bold",
            )
        return "CM-Regular", "CM-Bold"
