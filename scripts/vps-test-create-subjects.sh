#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
PASS="$(cat .admin-password)"
python3 - "$PASS" <<'PY'
import json, sys, urllib.request, urllib.error

password = sys.argv[1]

def call(method, url, token=None, body=None, extra_headers=None):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-Accounting-Demo-Token"] = token
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw[:800]}
        return e.code, payload

_, login = call("POST", "http://127.0.0.1:8096/api/admin/login", body={"username":"admin","password":password})
token = login["access_token"]

subject_body = {
    "name": "Test Odběratel s.r.o.",
    "email": "test-odberatel@example.com",
    "address": "Testovací 1, 11000 Praha",
    "phone": "+420777000000",
    "ico": "12345678",
    "dic": "CZ12345678",
    "data_box": None,
    "country": "CZ",
    "note": None,
}
supplier_body = {
    "name": "Test Dodavatel s.r.o.",
    "email": "test-dodavatel@example.com",
    "address": "Dodavatelská 2, 60200 Brno",
    "phone": "+420777000001",
    "ico": "87654321",
    "dic": "CZ87654321",
    "data_box": None,
    "country": "CZ",
    "note": None,
}

for label, path, body in [
    ("subject", "/api/accounting/subjects", subject_body),
    ("supplier", "/api/accounting/suppliers", supplier_body),
]:
    code, resp = call("POST", f"http://127.0.0.1:8096{path}", token=token, body=body)
    print(label, "POST", code, resp if code >= 400 else {"id": resp.get("id"), "name": resp.get("name"), "ico": resp.get("ico")})

code, subjects = call("GET", "http://127.0.0.1:8096/api/accounting/subjects", token=token)
code2, suppliers = call("GET", "http://127.0.0.1:8096/api/accounting/suppliers", token=token)
print("subjects_count", len(subjects) if isinstance(subjects, list) else subjects)
print("suppliers_count", len(suppliers) if isinstance(suppliers, list) else suppliers)

# ARES mock lookup
for ico in ("12345678", "75739593"):
    code, resp = call("GET", f"http://127.0.0.1:8096/api/accounting/ares/{ico}", token=token)
    print("ares", ico, code, resp if code >= 400 else {"name": resp.get("company_name"), "source": resp.get("source")})
PY

echo "=== LAST POST LINES ==="
docker compose -p pvm-deal logs --tail=50 accounting-backend 2>&1 | grep -E "POST|PUT|ERROR|Traceback|422|500" | tail -30
