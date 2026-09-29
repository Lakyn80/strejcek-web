"""Production ReportLab invoice PDF with Czech fonts, logo and SPAYD QR."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from accounting_api.database.models import Invoice
from accounting_api.domain.payments import build_czech_iban
from accounting_api.integrations.pdf import InvoicePdfDocument, InvoicePdfGenerationError
from accounting_api.integrations.spayd.payload import build_spayd_payload
from accounting_api.integrations.spayd.qr import ReportLabQrCodeRenderer
from accounting_api.services.export_dto import InvoiceExportDTO, build_invoice_export


@dataclass(frozen=True)
class InvoicePdfBranding:
    """Host-owned contact extras not snapshotted on Invoice rows."""

    issuer_email: str = ""
    issuer_phone: str = ""
    issuer_bic: str = ""
    issuer_website: str = ""
    logo_path: Path | None = None


# Czech bank code → BIC/SWIFT (without optional XXX branch suffix).
_CZECH_BANK_BIC: dict[str, str] = {
    "0100": "KOMBCZPP",  # Komerční banka
    "0300": "CEKOCZPP",  # ČSOB
    "0600": "AGBACZPP",  # Moneta
    "0800": "GIBACZPX",  # Česká spořitelna
    "2010": "FIOBCZPP",  # Fio
    "3030": "AIRACZPP",  # Air Bank
    "5500": "RZBCCZPP",  # Raiffeisenbank
    "6210": "BREXCZPP",  # mBank
}


def sanitize_invoice_pdf_filename(invoice_number: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_-]+", "-", (invoice_number or "draft").strip()) or "draft"
    return f"invoice-{cleaned}.pdf"


def resolve_issuer_bic(bank_code: str, configured_bic: str = "") -> str:
    """Prefer BIC derived from bank code; fall back to host branding."""
    mapped = _CZECH_BANK_BIC.get((bank_code or "").strip().zfill(4) if (bank_code or "").strip() else "")
    if mapped:
        return mapped
    return (configured_bic or "").strip().upper()


def resolve_invoice_iban(export: InvoiceExportDTO) -> str:
    iban = (export.payment.iban or "").strip().replace(" ", "").upper()
    if iban:
        return iban
    return build_czech_iban(
        account_number=export.payment.account_number,
        bank_code=export.payment.bank_code,
        account_prefix=export.payment.account_prefix,
    )


def build_invoice_spayd_payload(export: InvoiceExportDTO) -> str:
    return build_spayd_payload(
        iban=resolve_invoice_iban(export),
        amount=Decimal(export.totals.total),
        currency=export.totals.currency,
        variable_symbol=export.payment.variable_symbol,
        invoice_number=export.identity.invoice_number,
        due_date=export.identity.due_date,
    )


class ReportLabInvoicePdfGenerator:
    """Professional Czech invoice PDF driven by invoice export + host branding."""

    def __init__(
        self,
        *,
        branding: InvoicePdfBranding,
        storage_root: Path | None = None,
        persist: bool = True,
    ) -> None:
        self._branding = branding
        self._storage_root = storage_root.expanduser().resolve() if storage_root else None
        self._persist = persist
        self.last_spayd_payload: str | None = None

    def build_invoice_pdf(self, invoice: Invoice) -> InvoicePdfDocument:
        try:
            export = build_invoice_export(invoice)
            payload = build_invoice_spayd_payload(export)
            self.last_spayd_payload = payload
            content = self._render_pdf(export, payload)
        except InvoicePdfGenerationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surface as PDF generation error
            raise InvoicePdfGenerationError(f"PDF faktury se nepodařilo vytvořit: {exc}") from exc

        filename = sanitize_invoice_pdf_filename(export.identity.invoice_number)
        if self._persist and self._storage_root is not None:
            self._persist_pdf(filename, content)

        return InvoicePdfDocument(filename=filename, content=content, content_type="application/pdf")

    def _persist_pdf(self, filename: str, content: bytes) -> None:
        assert self._storage_root is not None
        target_dir = self._storage_root / "invoices"
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(filename).name
        (target_dir / safe_name).write_bytes(content)

    def _render_pdf(self, export: InvoiceExportDTO, spayd_payload: str) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        font_name, font_bold = _register_czech_fonts()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"Faktura {export.identity.invoice_number}",
            author=export.issuer.name,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=styles["Heading1"],
            fontName=font_bold,
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#111827"),
            spaceAfter=4,
        )
        section_style = ParagraphStyle(
            "InvoiceSection",
            parent=styles["Heading2"],
            fontName=font_bold,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "InvoiceBody",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1f2937"),
        )
        muted_style = ParagraphStyle(
            "InvoiceMuted",
            parent=body_style,
            textColor=colors.HexColor("#6b7280"),
            fontSize=8,
            leading=10,
        )
        right_style = ParagraphStyle("InvoiceRight", parent=body_style, alignment=TA_RIGHT)
        money_style = ParagraphStyle(
            "InvoiceMoney",
            parent=body_style,
            fontName=font_bold,
            fontSize=11,
            alignment=TA_RIGHT,
        )

        story: list[object] = []

        logo = _build_logo_image(self._branding.logo_path, max_width=42 * mm, max_height=18 * mm)
        header_left = logo if logo is not None else Paragraph("PVM-Deal", title_style)
        header_right = Paragraph(
            "<br/>".join(
                [
                    "<b>FAKTURA</b>",
                    f"č. {_escape(export.identity.invoice_number)}",
                    f"VS: {_escape(export.payment.variable_symbol)}",
                ]
            ),
            ParagraphStyle("HeaderRight", parent=body_style, alignment=TA_RIGHT, fontName=font_bold, fontSize=12, leading=16),
        )
        header_table = Table(
            [[header_left, header_right]],
            colWidths=[95 * mm, 75 * mm],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 6 * mm))

        issuer_para = Paragraph(_party_html(export, side="issuer", branding=self._branding), body_style)
        customer_para = Paragraph(_party_html(export, side="customer", branding=self._branding), body_style)
        parties = Table(
            [[issuer_para, customer_para]],
            colWidths=[85 * mm, 85 * mm],
        )
        parties.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOX", (0, 0), (0, 0), 0.4, colors.HexColor("#e5e7eb")),
                    ("BOX", (1, 0), (1, 0), 0.4, colors.HexColor("#e5e7eb")),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(parties)
        story.append(Spacer(1, 5 * mm))

        meta_data = [
            [Paragraph("Datum vystavení", muted_style), Paragraph(_fmt_date(export.identity.issue_date), body_style)],
            [Paragraph("Datum splatnosti", muted_style), Paragraph(_fmt_date(export.identity.due_date), body_style)],
            [Paragraph("Měna", muted_style), Paragraph(_escape(export.totals.currency), body_style)],
            [Paragraph("Způsob platby", muted_style), Paragraph(_escape(export.payment.method), body_style)],
            [Paragraph("Účet", muted_style), Paragraph(_escape(export.payment.account_label), body_style)],
            [Paragraph("IBAN", muted_style), Paragraph(_escape(resolve_invoice_iban(export)), body_style)],
        ]
        bic = resolve_issuer_bic(export.payment.bank_code, self._branding.issuer_bic)
        if bic:
            meta_data.append(
                [Paragraph("BIC/SWIFT", muted_style), Paragraph(_escape(bic), body_style)]
            )
        meta = Table(meta_data, colWidths=[45 * mm, 125 * mm])
        meta.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        story.append(Paragraph("Platební údaje a termíny", section_style))
        story.append(meta)
        story.append(Spacer(1, 4 * mm))

        show_vat = export.tax_mode != "reverse_charge" and Decimal(export.totals.vat_amount) > 0
        item_header = (
            ["Popis", "Množství", "Cena bez DPH", "DPH", "Celkem"]
            if show_vat
            else ["Popis", "Množství", "Jedn. cena", "Celkem"]
        )
        rows: list[list[object]] = [[Paragraph(_escape(h), muted_style) for h in item_header]]
        for item in export.items:
            if show_vat:
                line_base = Decimal(item.line_total)
                rate = Decimal(export.totals.vat_rate or 0)
                line_vat = _quantize_line_vat(line_base, rate)
                line_gross = line_base + line_vat
                rows.append(
                    [
                        Paragraph(_escape(item.description), body_style),
                        Paragraph(_fmt_qty(Decimal(item.quantity)), right_style),
                        Paragraph(_fmt_money(line_base), right_style),
                        Paragraph(_fmt_money(line_vat), right_style),
                        Paragraph(_fmt_money(line_gross), right_style),
                    ]
                )
            else:
                rows.append(
                    [
                        Paragraph(_escape(item.description), body_style),
                        Paragraph(_fmt_qty(Decimal(item.quantity)), right_style),
                        Paragraph(_fmt_money(Decimal(item.unit_price)), right_style),
                        Paragraph(_fmt_money(Decimal(item.line_total)), right_style),
                    ]
                )
        col_widths = (
            [70 * mm, 22 * mm, 28 * mm, 25 * mm, 29 * mm]
            if show_vat
            else [90 * mm, 25 * mm, 30 * mm, 29 * mm]
        )

        items_table = Table(rows, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), font_bold),
                    ("FONTNAME", (0, 1), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ]
            )
        )
        story.append(Paragraph("Položky", section_style))
        story.append(items_table)
        story.append(Spacer(1, 4 * mm))

        totals_rows = [
            [Paragraph("Základ", body_style), Paragraph(f"{_fmt_money(Decimal(export.totals.subtotal))} {_escape(export.totals.currency)}", right_style)],
        ]
        if show_vat:
            rate_label = f"DPH {export.totals.vat_rate} %" if export.totals.vat_rate is not None else "DPH"
            totals_rows.append(
                [
                    Paragraph(rate_label, body_style),
                    Paragraph(
                        f"{_fmt_money(Decimal(export.totals.vat_amount))} {_escape(export.totals.currency)}",
                        right_style,
                    ),
                ]
            )
        elif export.tax_mode == "reverse_charge":
            totals_rows.append(
                [
                    Paragraph("Režim DPH", body_style),
                    Paragraph(_escape(export.reverse_charge_text or "Přenesená daňová povinnost"), right_style),
                ]
            )
        else:
            totals_rows.append(
                [
                    Paragraph("Režim DPH", body_style),
                    Paragraph("Bez DPH", right_style),
                ]
            )
        totals_rows.append(
            [
                Paragraph("Celkem k úhradě", money_style),
                Paragraph(
                    f"{_fmt_money(Decimal(export.totals.total))} {_escape(export.totals.currency)}",
                    money_style,
                ),
            ]
        )
        totals = Table(totals_rows, colWidths=[110 * mm, 60 * mm])
        totals.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfdf5")),
                    ("BOX", (0, -1), (-1, -1), 0.8, colors.HexColor("#059669")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        qr_drawing = ReportLabQrCodeRenderer().render(spayd_payload, size_mm=36.0)
        story.append(Spacer(1, 3 * mm))
        story.append(totals)
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("QR platba (SPD 1.0)", section_style))
        story.append(qr_drawing)
        story.append(Paragraph("Naskenujte v bankovní aplikaci", muted_style))

        if export.note:
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph("Poznámka", section_style))
            story.append(Paragraph(_escape(export.note), body_style))

        story.append(Spacer(1, 8 * mm))
        story.append(
            Paragraph(
                "Doklad byl vytvořen v PVM-Deal Accounting. QR kód obsahuje platební instrukci SPD 1.0.",
                muted_style,
            )
        )

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        if not pdf_bytes.startswith(b"%PDF"):
            raise InvoicePdfGenerationError("Vygenerovaný soubor není validní PDF.")
        return pdf_bytes


def _register_czech_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Prefer DejaVu on Linux/Docker (production); Arial on Windows local.
    candidates = [
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            "PvmDejaVu",
            "PvmDejaVuBold",
        ),
        (
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\arialbd.ttf"),
            "PvmArial",
            "PvmArialBold",
        ),
        (
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
            "PvmLiberation",
            "PvmLiberationBold",
        ),
    ]
    for regular, bold, regular_name, bold_name in candidates:
        if regular.is_file() and bold.is_file():
            registered = set(pdfmetrics.getRegisteredFontNames())
            if regular_name not in registered:
                pdfmetrics.registerFont(TTFont(regular_name, str(regular)))
            if bold_name not in registered:
                pdfmetrics.registerFont(TTFont(bold_name, str(bold)))
            return regular_name, bold_name
    raise InvoicePdfGenerationError(
        "Chybí font s podporou češtiny (DejaVu/Arial). PDF by zobrazovalo poškozené háčky a čárky."
    )


def _build_logo_image(logo_path: Path | None, *, max_width: float, max_height: float):
    if logo_path is None or not logo_path.is_file():
        return None
    try:
        from reportlab.platypus import Image
        from PIL import Image as PILImage

        with PILImage.open(logo_path) as img:
            img = img.convert("RGBA")
            # Downscale large assets for PDF embedding.
            img.thumbnail((900, 360))
            tmp = io.BytesIO()
            img.save(tmp, format="PNG")
            tmp.seek(0)
            width, height = img.size
        scale = min(max_width / float(width), max_height / float(height), 1.0)
        return Image(tmp, width=width * scale, height=height * scale)
    except Exception:
        return None


def _party_html(export: InvoiceExportDTO, *, side: str, branding: InvoicePdfBranding) -> str:
    if side == "issuer":
        lines = [
            "<b>Dodavatel</b>",
            _escape(export.issuer.name),
            _escape(_format_address(export.issuer.address, export.issuer.zip, export.issuer.city)),
        ]
        if export.issuer.ico:
            lines.append(f"IČO: {_escape(export.issuer.ico)}")
        if export.issuer.dic:
            lines.append(f"DIČ: {_escape(export.issuer.dic)}")
        if branding.issuer_email:
            lines.append(_escape(branding.issuer_email))
        if branding.issuer_phone:
            lines.append(_escape(branding.issuer_phone))
        if branding.issuer_website:
            lines.append(_escape(branding.issuer_website))
        return "<br/>".join(line for line in lines if line)
    lines = [
        "<b>Odběratel</b>",
        _escape(export.customer.name),
        _escape(export.customer.address or ""),
    ]
    if export.customer.ico:
        lines.append(f"IČO: {_escape(export.customer.ico)}")
    if export.customer.dic:
        lines.append(f"DIČ: {_escape(export.customer.dic)}")
    if export.customer.email:
        lines.append(_escape(export.customer.email))
    if export.customer.phone:
        lines.append(_escape(export.customer.phone))
    return "<br/>".join(line for line in lines if line)


def _format_address(address: str, zip_code: str, city: str) -> str:
    city_line = " ".join(part for part in (zip_code.strip(), city.strip()) if part)
    parts = [address.strip(), city_line]
    return ", ".join(part for part in parts if part)


def _escape(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt_date(value) -> str:
    return value.strftime("%d.%m.%Y")


def _fmt_money(value: Decimal) -> str:
    quantized = Decimal(value).quantize(Decimal("0.01"))
    return f"{quantized:,.2f}".replace(",", " ").replace(".", ",")


def _fmt_qty(value: Decimal) -> str:
    text = f"{Decimal(value):.3f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def _quantize_line_vat(line_base: Decimal, rate: Decimal) -> Decimal:
    return (Decimal(line_base) * Decimal(rate) / Decimal("100")).quantize(Decimal("0.01"))
