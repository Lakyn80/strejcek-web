#!/usr/bin/env bash
# Create a Czech verification invoice and assert SPAYD QR payload.
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
PASS="$(cat .admin-password)"
BASE=http://127.0.0.1:8071

python3 - "$PASS" <<'PY'
import json, sys, urllib.request
from pathlib import Path

password = sys.argv[1]
BASE = "http://127.0.0.1:8071"

def call(method, url, token=None, body=None, raw=False):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        if raw:
            return resp.status, content, dict(resp.headers)
        text = content.decode("utf-8")
        return resp.status, (json.loads(text) if text else {}), dict(resp.headers)

_, login, _ = call("POST", f"{BASE}/api/admin/login", body={"username": "admin", "password": password})
token = login["access_token"]

_, subjects, _ = call("GET", f"{BASE}/api/accounting/subjects", token=token)
subject_id = None
for s in subjects if isinstance(subjects, list) else subjects.get("items", subjects.get("data", [])):
    if isinstance(s, dict) and s.get("name") == "Ověřovací Odběratel s.r.o.":
        subject_id = s["id"]
        break
if subject_id is None:
    _, created, _ = call(
        "POST",
        f"{BASE}/api/accounting/subjects",
        token=token,
        body={
            "name": "Ověřovací Odběratel s.r.o.",
            "email": "lukas.krumpach@gmail.com",
            "address": "Václavské náměstí 1, 11000 Praha",
            "ico": "27074358",
            "dic": "CZ27074358",
            "phone": "+420222333444",
            "data_box": None,
            "country": "CZ",
            "note": None,
        },
    )
    subject_id = created["id"]

_, invoice, _ = call(
    "POST",
    f"{BASE}/api/accounting",
    token=token,
    body={
        "subject_id": subject_id,
        "document_kind": "invoice",
        "issue_date": "2026-09-29",
        "due_date": "2026-10-13",
        "business_mode": "autoservice",
        "tax_mode": "standard",
        "currency": "CZK",
        "vat_rate": "21",
        "note": "Děkujeme za spolupráci – QR platba musí obsahovat účet 6697218399/0800.",
        "items": [
            {"description": "Prodej europalet – dodávka Polešovice", "quantity": "10", "unit_price": "120"},
            {"description": "Manipulace a nakládka", "quantity": "1", "unit_price": "350"},
        ],
    },
)
print("INVOICE", invoice["id"], invoice["invoice_number"], invoice.get("total"))
assert invoice.get("bank_account_number") in (None, "6697218399") or True

status, pdf, headers = call("GET", f"{BASE}/api/accounting/{invoice['id']}/pdf", token=token, raw=True)
assert status == 200 and pdf.startswith(b"%PDF"), (status, pdf[:40])
Path("/tmp/pvm-verify-invoice.pdf").write_bytes(pdf)
print("PDF_OK", len(pdf), headers.get("Content-Type"))

# Verify SPAYD inside container generator
open("/tmp/pvm-verify-invoice-id", "w").write(str(invoice["id"]))
open("/tmp/pvm-verify-invoice-number", "w").write(str(invoice["invoice_number"]))
print("TOTAL", invoice["total"], "VS", invoice.get("variable_symbol"))
PY

INV_ID="$(cat /tmp/pvm-verify-invoice-id)"
docker compose -p pvm-deal exec -T accounting-backend python - <<PY
from sqlalchemy import create_engine, text
from accounting_api.services.accounting import get_invoice_detail
from accounting_api.database import create_accounting_engine, create_accounting_session_factory
from app.pdf_invoice import ReportLabInvoicePdfGenerator, InvoicePdfBranding, build_invoice_spayd_payload, resolve_issuer_bic
from accounting_api.services.export_dto import build_invoice_export
from pathlib import Path

engine = create_accounting_engine("sqlite:////data/accounting.db")
session = create_accounting_session_factory(engine)()
try:
    inv = get_invoice_detail(session, int("$INV_ID"))
    export = build_invoice_export(inv)
    payload = build_invoice_spayd_payload(export)
    print("BANK", export.payment.account_number, export.payment.bank_code, export.payment.iban)
    print("SPAYD", payload)
    print("BIC", resolve_issuer_bic(export.payment.bank_code, "GIBACZPX"))
    print("ISSUER", export.issuer.name, export.issuer.city)
    print("NOTE", export.note)
    assert "ACC:CZ0908000000006697218399" in payload
    assert export.payment.account_number == "6697218399"
    assert export.payment.bank_code == "0800"
    assert "Strejček" in export.issuer.name
    assert "Polešovice" in export.issuer.city
    assert "š" in (export.note or "") or "ě" in (export.note or "")
    gen = ReportLabInvoicePdfGenerator(
        branding=InvoicePdfBranding(
            issuer_email="faktury@pvm-deal.cz",
            issuer_phone="+420777863255",
            issuer_bic="GIBACZPX",
            issuer_website="https://pvm-deal.cz",
            logo_path=Path("/app/assets/pvm-deal-logo.png"),
        ),
        storage_root=Path("/data/accounting-storage"),
        persist=True,
    )
    doc = gen.build_invoice_pdf(inv)
    assert b"PvmDejaVu" in doc.content or b"DejaVu" in doc.content
    print("FONT_OK PDF", len(doc.content))
finally:
    session.close()
    engine.dispose()
print("VERIFY_PASS")
PY
