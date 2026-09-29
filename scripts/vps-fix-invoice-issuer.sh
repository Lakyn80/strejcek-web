#!/usr/bin/env bash
# Fix production invoice issuer branding + bank snapshots for QR payments.
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

umask 077
python3 <<'PY'
from pathlib import Path

path = Path("accounting.env")
text = path.read_text(encoding="utf-8") if path.exists() else ""
lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
kv = {}
for ln in lines:
    if "=" in ln:
        k, v = ln.split("=", 1)
        kv[k] = v

kv["ACCOUNTING_ISSUER_BIC"] = "GIBACZPX"
kv["ACCOUNTING_ISSUER_WEBSITE"] = "https://pvm-deal.cz"
kv["ACCOUNTING_ISSUER_PHONE_FALLBACK"] = "+420777863255"
# keep existing keys; ensure email provider stays
if "ACCOUNTING_EMAIL_PROVIDER" not in kv:
    kv["ACCOUNTING_EMAIL_PROVIDER"] = "resend"

# Preserve SECRET / hashes exactly; rewrite file preserving known order + extras
preferred = [
    "ADMIN_USERNAME",
    "ADMIN_PASSWORD_HASH",
    "ADMIN_DISPLAY_NAME",
    "ADMIN_EMAIL",
    "SECRET_KEY",
    "ADMIN_ALLOWED_ORIGINS",
    "ACCOUNTING_EMAIL_PROVIDER",
    "ACCOUNTING_EMAIL_FROM",
    "RESEND_API_KEY",
    "RESEND_FROM_EMAIL",
    "RESEND_FROM_NAME",
    "ACCOUNTING_INVOICE_COPY_EMAIL",
    "ACCOUNTING_ARES_PROVIDER",
    "ACCOUNTING_ISSUER_BIC",
    "ACCOUNTING_ISSUER_WEBSITE",
    "ACCOUNTING_ISSUER_PHONE_FALLBACK",
]
out = []
seen = set()
for key in preferred:
    if key in kv:
        out.append(f"{key}={kv[key]}")
        seen.add(key)
for key, val in kv.items():
    if key not in seen:
        out.append(f"{key}={val}")
path.write_text("\n".join(out) + "\n", encoding="utf-8")
path.chmod(0o600)
print("accounting.env updated (BIC/phone)")
PY

PASS="$(cat .admin-password)"
python3 - "$PASS" <<'PY'
import json, sys, urllib.request

password = sys.argv[1]
BASE = "http://127.0.0.1:8071"

def call(method, url, token=None, body=None):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}

token = call("POST", f"{BASE}/api/admin/login", body={"username": "admin", "password": password})["access_token"]
settings = call("GET", f"{BASE}/api/accounting/settings", token=token)
settings["default_note"] = "Děkujeme za spolupráci."
settings["payment_method"] = "Převodem"
settings["bank_account_number"] = "6697218399"
settings["bank_account_prefix"] = None
settings["bank_code"] = "0800"
settings["bank_iban"] = "CZ0908000000006697218399"
settings["issuer_name"] = "Robin Strejček"
settings["issuer_address"] = "Polešovice 483"
settings["issuer_city"] = "Polešovice"
settings["issuer_zip"] = "68737"
settings["issuer_ico"] = "75739593"
settings["issuer_dic"] = settings.get("issuer_dic") or ""
settings["issuer_email"] = "robin.strejcek@centrum.cz"
settings["issuer_phone"] = "+420777863255"
settings["owner_email"] = "robin.strejcek@centrum.cz"
# API may reject unknown keys – keep only known
allowed = {
    "owner_email","issuer_name","issuer_address","issuer_city","issuer_zip","issuer_ico","issuer_dic",
    "issuer_data_box","issuer_email","issuer_phone","default_currency","default_due_days","default_note",
    "payment_method","bank_account_number","bank_account_prefix","bank_code","bank_iban",
}
payload = {k: settings.get(k) for k in allowed}
saved = call("PUT", f"{BASE}/api/accounting/settings", token=token, body=payload)
print("SETTINGS_OK", saved.get("account_label"), saved.get("bank_iban"), saved.get("issuer_name"))
open("/tmp/pvm-fa-token","w",encoding="utf-8").write(token)
PY

docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from sqlalchemy import create_engine, text
eng = create_engine("sqlite:////data/accounting.db")
with eng.begin() as c:
    result = c.execute(
        text(
            """
            UPDATE invoices
            SET bank_account_number = :acc,
                bank_account_prefix = NULL,
                bank_code = :bank,
                bank_iban = :iban,
                payment_method = :method,
                issuer_name = :name,
                issuer_address = :addr,
                issuer_city = :city,
                issuer_zip = :zip,
                issuer_ico = :ico
            """
        ),
        {
            "acc": "6697218399",
            "bank": "0800",
            "iban": "CZ0908000000006697218399",
            "method": "Převodem",
            "name": "Robin Strejček",
            "addr": "Polešovice 483",
            "city": "Polešovice",
            "zip": "68737",
            "ico": "75739593",
        },
    )
    print("invoices_updated", result.rowcount)
PY

echo "DB_AND_SETTINGS_DONE"
