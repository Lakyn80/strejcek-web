#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
echo "=== CONTAINERS ==="
docker compose -p pvm-deal ps
echo "=== RECENT ERRORS ==="
docker compose -p pvm-deal logs --tail=300 accounting-backend 2>&1 | grep -E "ERROR|Error|Traceback|500|subjects|suppliers|settings|Exception" | tail -80
echo "=== API SMOKE ==="
PASS="$(cat .admin-password)"
python3 - "$PASS" <<'PY'
import json, sys, urllib.request, urllib.error

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
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw[:500]}
        return exc.code, payload

_, login = call("POST", "http://127.0.0.1:8096/api/admin/login", body={"username":"admin","password":password})
token = login.get("access_token")
print("LOGIN", bool(token))

for path in [
    "/api/accounting/settings",
    "/api/accounting/subjects",
    "/api/accounting/suppliers",
    "/api/accounting",
]:
    code, body = call("GET", f"http://127.0.0.1:8096{path}", token=token)
    print("GET", path, code, type(body).__name__, (list(body)[:5] if isinstance(body, dict) else f"len={len(body)}" if isinstance(body, list) else body))

# try create subject
code, body = call("POST", "http://127.0.0.1:8096/api/accounting/subjects", token=token, body={
    "name": "Test Odběratel s.r.o.",
    "ico": "12345678",
    "dic": "CZ12345678",
    "address_line": "Testovací 1",
    "city": "Praha",
    "zip": "11000",
    "country": "Česká republika",
    "email": "test@example.com",
    "phone": "+420777000000",
})
print("POST subject", code, body)

code, body = call("POST", "http://127.0.0.1:8096/api/accounting/suppliers", token=token, body={
    "name": "Test Dodavatel s.r.o.",
    "ico": "87654321",
    "dic": "CZ87654321",
    "address_line": "Dodavatelská 2",
    "city": "Brno",
    "zip": "60200",
    "country": "Česká republika",
    "email": "supplier@example.com",
    "phone": "+420777000001",
})
print("POST supplier", code, body)
PY
