#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
PASS="$(cat .admin-password)"

python3 - "$PASS" <<'PY'
import json, sys, urllib.request

password = sys.argv[1]

def call(method, url, token=None, body=None):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw}
        print("HTTP_ERROR", exc.code, payload)
        raise SystemExit(1)

_, login = call("POST", "http://127.0.0.1:8096/api/admin/login", body={
    "username": "admin",
    "password": password,
})
token = login["access_token"]

payload = {
    "owner_email": "robin.strejcek@centrum.cz",
    "issuer_name": "Robin Strejček",
    "issuer_address": "Polešovice 483",
    "issuer_city": "Polešovice",
    "issuer_zip": "68737",
    "issuer_ico": "75739593",
    "issuer_dic": None,
    "issuer_data_box": None,
    "issuer_email": "robin.strejcek@centrum.cz",
    "issuer_phone": "+420777863255",
    "default_currency": "CZK",
    "default_due_days": 14,
    "default_note": None,
    "payment_method": "Převodem",
    # Placeholder bank – replace with real account in admin UI
    "bank_account_number": "0000000000",
    "bank_account_prefix": None,
    "bank_code": "0100",
    "bank_iban": None,
}

status, saved = call(
    "PUT",
    "http://127.0.0.1:8096/api/accounting/settings",
    token=token,
    body=payload,
)
print("PUT_STATUS", status)
print("SAVED_ICO", saved.get("issuer_ico"))
print("SAVED_NAME", saved.get("issuer_name"))

status, loaded = call(
    "GET",
    "http://127.0.0.1:8096/api/accounting/settings",
    token=token,
)
print("GET_STATUS", status)
print("GET_ICO", loaded.get("issuer_ico"))
print("SETTINGS_OK")
PY
