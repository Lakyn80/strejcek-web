from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from accounting_api.integrations.pdf import configure_pdf_generator

from app.main import EMPTY_INVOICE_SETTINGS_RESPONSE
from app.pdf_invoice import InvoicePdfBranding, ReportLabInvoicePdfGenerator

from .test_invoice_pdf_workflow import (
    SETTINGS_PAYLOAD,
    auth_client,
    create_subject,
    seed_settings,
)


INVOICE_ITEMS = [
    {"description": "Servisní práce – výměna filtru", "quantity": "1", "unit_price": "1000"},
    {"description": "Materiál", "quantity": "2", "unit_price": "250.50"},
]
EXPECTED_SUBTOTAL = Decimal("1501.00")


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_invoice(
    client: TestClient,
    token: str,
    subject_id: int,
    *,
    vat_rate: str = "21",
) -> dict:
    response = client.post(
        "/api/accounting",
        headers=_auth_headers(token),
        json={
            "subject_id": subject_id,
            "document_kind": "invoice",
            "issue_date": "2026-09-28",
            "due_date": "2026-10-12",
            "business_mode": "autoservice",
            "tax_mode": "standard",
            "currency": "CZK",
            "vat_rate": vat_rate,
            "note": "VAT mode test",
            "items": INVOICE_ITEMS,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _put_settings(client: TestClient, token: str, **overrides: object) -> dict:
    payload = {**SETTINGS_PAYLOAD, **overrides}
    response = client.put(
        "/api/accounting/settings",
        headers=_auth_headers(token),
        json=payload,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _get_settings(client: TestClient, token: str) -> dict:
    response = client.get("/api/accounting/settings", headers=_auth_headers(token))
    assert response.status_code == 200, response.text
    return response.json()


def _install_tracking_pdf_generator(settings) -> ReportLabInvoicePdfGenerator:
    generator = ReportLabInvoicePdfGenerator(
        branding=InvoicePdfBranding(
            issuer_email="accounting@example.test",
            issuer_phone="+420777863255",
            issuer_bic="GIBACZPX",
            issuer_website="https://pvm-deal.cz",
            logo_path=settings.accounting_logo_path if settings.accounting_logo_path.is_file() else None,
        ),
        storage_root=settings.ensure_storage_directory(),
        persist=True,
    )
    configure_pdf_generator(generator)
    return generator


def test_settings_default_vat_enabled_false_when_omitted(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    payload = {k: v for k, v in SETTINGS_PAYLOAD.items() if k != "vat_enabled"}
    assert "vat_enabled" not in payload

    put_response = client.put(
        "/api/accounting/settings",
        headers=_auth_headers(token),
        json=payload,
    )
    assert put_response.status_code == 200, put_response.text
    assert put_response.json()["vat_enabled"] is False

    got = _get_settings(client, token)
    assert got["vat_enabled"] is False


def test_put_settings_vat_enabled_false_persists(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=True)

    saved = _put_settings(client, token, vat_enabled=False)
    assert saved["vat_enabled"] is False
    assert _get_settings(client, token)["vat_enabled"] is False


def test_put_settings_vat_enabled_true_persists(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=False)

    saved = _put_settings(client, token, vat_enabled=True)
    assert saved["vat_enabled"] is True
    assert _get_settings(client, token)["vat_enabled"] is True


def test_create_invoice_vat_disabled_ignores_client_vat_rate(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=False)
    subject_id = create_subject(client, token)

    invoice = _create_invoice(client, token, subject_id, vat_rate="21")

    assert Decimal(str(invoice["subtotal"])) == EXPECTED_SUBTOTAL
    assert Decimal(str(invoice["vat_amount"])) == Decimal("0.00")
    assert Decimal(str(invoice["vat_rate"])) == Decimal("0")
    assert Decimal(str(invoice["total"])) == EXPECTED_SUBTOTAL


def test_create_invoice_vat_enabled_rate_21(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=True)
    subject_id = create_subject(client, token)

    invoice = _create_invoice(client, token, subject_id, vat_rate="21")

    assert Decimal(str(invoice["subtotal"])) == EXPECTED_SUBTOTAL
    assert Decimal(str(invoice["vat_rate"])) == Decimal("21.00")
    assert Decimal(str(invoice["vat_amount"])) == Decimal("315.21")
    assert Decimal(str(invoice["total"])) == Decimal("1816.21")


def test_create_invoice_vat_enabled_rate_12(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=True)
    subject_id = create_subject(client, token)

    invoice = _create_invoice(client, token, subject_id, vat_rate="12")

    assert Decimal(str(invoice["subtotal"])) == EXPECTED_SUBTOTAL
    assert Decimal(str(invoice["vat_rate"])) == Decimal("12.00")
    assert Decimal(str(invoice["vat_amount"])) == Decimal("180.12")
    assert Decimal(str(invoice["total"])) == Decimal("1681.12")


def test_pdf_without_vat_spayd_am_equals_subtotal(tmp_path: Path) -> None:
    client, token, settings = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=False)
    subject_id = create_subject(client, token)
    invoice = _create_invoice(client, token, subject_id, vat_rate="21")
    assert Decimal(str(invoice["vat_amount"])) == Decimal("0.00")

    generator = _install_tracking_pdf_generator(settings)
    pdf = client.get(
        f"/api/accounting/{invoice['id']}/pdf",
        headers=_auth_headers(token),
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")

    assert generator.last_spayd_payload is not None
    assert f"AM:{EXPECTED_SUBTOTAL:.2f}" in generator.last_spayd_payload
    assert f"AM:{Decimal(str(invoice['total'])):.2f}" in generator.last_spayd_payload


def test_pdf_with_vat_spayd_am_equals_total_including_vat(tmp_path: Path) -> None:
    client, token, settings = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=True)
    subject_id = create_subject(client, token)
    invoice = _create_invoice(client, token, subject_id, vat_rate="21")
    expected_total = Decimal("1816.21")
    assert Decimal(str(invoice["total"])) == expected_total
    assert Decimal(str(invoice["vat_amount"])) == Decimal("315.21")

    generator = _install_tracking_pdf_generator(settings)
    pdf = client.get(
        f"/api/accounting/{invoice['id']}/pdf",
        headers=_auth_headers(token),
    )
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")

    assert generator.last_spayd_payload is not None
    assert f"AM:{expected_total:.2f}" in generator.last_spayd_payload


def test_disabling_vat_does_not_rewrite_existing_invoice(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token, vat_enabled=True)
    subject_id = create_subject(client, token)
    invoice = _create_invoice(client, token, subject_id, vat_rate="21")

    original_vat = Decimal(str(invoice["vat_amount"]))
    original_total = Decimal(str(invoice["total"]))
    original_rate = Decimal(str(invoice["vat_rate"]))
    assert original_vat == Decimal("315.21")
    assert original_total == Decimal("1816.21")

    _put_settings(client, token, vat_enabled=False)
    assert _get_settings(client, token)["vat_enabled"] is False

    detail = client.get(
        f"/api/accounting/{invoice['id']}",
        headers=_auth_headers(token),
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert Decimal(str(body["vat_amount"])) == original_vat
    assert Decimal(str(body["total"])) == original_total
    assert Decimal(str(body["vat_rate"])) == original_rate
    assert Decimal(str(body["subtotal"])) == EXPECTED_SUBTOTAL


def test_empty_settings_response_includes_vat_enabled_false(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)

    response = client.get("/api/accounting/settings", headers=_auth_headers(token))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["vat_enabled"] is False
    assert body == EMPTY_INVOICE_SETTINGS_RESPONSE
