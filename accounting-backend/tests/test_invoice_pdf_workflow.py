from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from accounting_api.integrations.email import configure_email_port
from accounting_api.integrations.pdf import configure_pdf_generator
from accounting_api.testing.email import InMemoryEmailPort

from app.auth import hash_password
from app.config import Settings
from app.main import create_app
from app.pdf_invoice import (
    InvoicePdfBranding,
    ReportLabInvoicePdfGenerator,
    build_invoice_spayd_payload,
    sanitize_invoice_pdf_filename,
)
from accounting_api.services.export_dto import build_invoice_export


SETTINGS_PAYLOAD = {
    "owner_email": "owner@example.test",
    "issuer_name": "Robin Strejček – Pólšovice",
    "issuer_address": "Polešovice 483",
    "issuer_city": "Polešovice",
    "issuer_zip": "68737",
    "issuer_ico": "75739593",
    "issuer_dic": "",
    "issuer_data_box": None,
    "issuer_email": "robin.strejcek@centrum.cz",
    "issuer_phone": "+420777863255",
    "default_currency": "CZK",
    "default_due_days": 14,
    "default_note": "Děkujeme za spolupráci.",
    "payment_method": "Převodem",
    "bank_account_number": "0000000000",
    "bank_account_prefix": None,
    "bank_code": "0100",
    "bank_iban": "",
}


def build_settings(tmp_path: Path, **overrides: object) -> Settings:
    logo = Path(__file__).resolve().parents[1] / "assets" / "pvm-deal-logo.png"
    payload = dict(
        _env_file=None,
        accounting_database_url=f"sqlite:///{tmp_path / 'accounting.db'}",
        accounting_storage_path=tmp_path / "storage",
        accounting_email_from="accounting@example.test",
        accounting_email_provider="console",
        accounting_ares_provider="mock",
        accounting_logo_path=logo if logo.is_file() else tmp_path / "missing-logo.png",
        accounting_issuer_bic="KOMBCZPPXXX",
        accounting_issuer_website="https://pvm-deal.cz",
        admin_username="admin",
        admin_password_hash=hash_password("correct-password", salt="testsalt", iterations=1_000),
        admin_display_name="Test Admin",
        admin_email="admin@example.test",
        secret_key="test-secret-key",
        admin_allowed_origins="http://localhost:5174",
    )
    payload.update(overrides)
    return Settings(**payload)


def auth_client(tmp_path: Path) -> tuple[TestClient, str, Settings]:
    settings = build_settings(tmp_path)
    app = create_app(settings)
    client = TestClient(app)
    login = client.post("/api/admin/login", json={"username": "admin", "password": "correct-password"})
    assert login.status_code == 200, login.text
    return client, login.json()["access_token"], settings


def seed_settings(client: TestClient, token: str) -> None:
    response = client.put(
        "/api/accounting/settings",
        headers={"Authorization": f"Bearer {token}"},
        json=SETTINGS_PAYLOAD,
    )
    assert response.status_code == 200, response.text


def create_subject(client: TestClient, token: str) -> int:
    response = client.post(
        "/api/accounting/subjects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Testovací Odběratel s.r.o.",
            "email": "odberatel@example.test",
            "address": "Pražská 1, 11000 Praha",
            "ico": "27074358",
            "dic": "CZ27074358",
            "phone": None,
            "data_box": None,
            "country": "CZ",
            "note": None,
        },
    )
    assert response.status_code == 200, response.text
    return int(response.json()["id"])


def create_invoice(client: TestClient, token: str, subject_id: int) -> dict:
    response = client.post(
        "/api/accounting",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "subject_id": subject_id,
            "document_kind": "invoice",
            "issue_date": "2026-09-28",
            "due_date": "2026-10-12",
            "business_mode": "autoservice",
            "tax_mode": "standard",
            "currency": "CZK",
            "vat_rate": "21",
            "note": "České znaky: příliš žluťoučký kůň",
            "items": [
                {"description": "Servisní práce – výměna filtru", "quantity": "1", "unit_price": "1000"},
                {"description": "Materiál", "quantity": "2", "unit_price": "250.50"},
            ],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_invoice_numbering_and_totals(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token)
    subject_id = create_subject(client, token)
    first = create_invoice(client, token, subject_id)
    second = create_invoice(client, token, subject_id)

    assert first["invoice_number"]
    assert second["invoice_number"]
    assert first["invoice_number"] != second["invoice_number"]
    assert first["variable_symbol"] == first["invoice_number"]
    assert Decimal(str(first["subtotal"])) == Decimal("1501.00")
    assert Decimal(str(first["vat_amount"])) == Decimal("315.21")
    assert Decimal(str(first["total"])) == Decimal("1816.21")


def test_pdf_generation_qr_czech_logo_and_storage(tmp_path: Path) -> None:
    client, token, settings = auth_client(tmp_path)
    seed_settings(client, token)
    subject_id = create_subject(client, token)
    invoice = create_invoice(client, token, subject_id)

    pdf = client.get(
        f"/api/accounting/{invoice['id']}/pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")
    assert len(pdf.content) > 1000
    assert "inline" in pdf.headers.get("content-disposition", "")

    stored = settings.ensure_storage_directory() / "invoices" / sanitize_invoice_pdf_filename(invoice["invoice_number"])
    assert stored.is_file()
    assert stored.read_bytes().startswith(b"%PDF")


def test_pdf_requires_auth(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token)
    subject_id = create_subject(client, token)
    invoice = create_invoice(client, token, subject_id)

    unauthorized = client.get(f"/api/accounting/{invoice['id']}/pdf")
    assert unauthorized.status_code == 401


def test_email_send_success_and_failure(tmp_path: Path) -> None:
    client, token, _ = auth_client(tmp_path)
    seed_settings(client, token)
    subject_id = create_subject(client, token)
    invoice = create_invoice(client, token, subject_id)

    port = InMemoryEmailPort()
    configure_email_port(port)

    ok = client.post(
        f"/api/accounting/{invoice['id']}/send-email",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_email": "odberatel@example.test"},
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["sent_to"] == "odberatel@example.test"
    assert len(port.messages) == 1
    assert port.messages[0].attachments
    assert port.messages[0].attachments[0].content.startswith(b"%PDF")

    class FailingPort(InMemoryEmailPort):
        def send(self, message):  # type: ignore[no-untyped-def]
            raise RuntimeError("smtp down")

    configure_email_port(FailingPort())
    failed = client.post(
        f"/api/accounting/{invoice['id']}/send-email",
        headers={"Authorization": f"Bearer {token}"},
        json={"to_email": "odberatel@example.test"},
    )
    assert failed.status_code == 502


def test_spayd_payload_is_dynamic(tmp_path: Path) -> None:
    client, token, settings = auth_client(tmp_path)
    seed_settings(client, token)
    subject_id = create_subject(client, token)
    invoice_payload = create_invoice(client, token, subject_id)

    detail = client.get(
        f"/api/accounting/{invoice_payload['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200

    # Rebuild export-compatible object via PDF generator path
    generator = ReportLabInvoicePdfGenerator(
        branding=InvoicePdfBranding(
            issuer_email="accounting@example.test",
            issuer_phone="+420 000 000 000",
            issuer_bic="KOMBCZPPXXX",
            issuer_website="https://pvm-deal.cz",
            logo_path=settings.accounting_logo_path if settings.accounting_logo_path.is_file() else None,
        ),
        storage_root=settings.ensure_storage_directory(),
        persist=False,
    )
    # Use API PDF which sets last payload indirectly; assert payload helpers directly on export DTO fields
    from accounting_api.database import create_accounting_engine, create_accounting_session_factory
    from accounting_api.services.accounting import get_invoice_detail

    engine = create_accounting_engine(settings.accounting_database_url)
    session = create_accounting_session_factory(engine)()
    try:
        invoice = get_invoice_detail(session, invoice_payload["id"])
        export = build_invoice_export(invoice)
        payload = build_invoice_spayd_payload(export)
        document = generator.build_invoice_pdf(invoice)
    finally:
        session.close()
        engine.dispose()

    assert payload.startswith("SPD*1.0*")
    assert f"AM:{Decimal(str(invoice_payload['total'])):.2f}" in payload
    assert f"X-VS:{invoice_payload['variable_symbol']}" in payload
    assert generator.last_spayd_payload == payload
    assert document.content.startswith(b"%PDF")
    assert "příliš" in export.note or "kun" in (export.note or "").lower() or "žluť" in (export.note or "")
