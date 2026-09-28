#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
python3 - "$TAG" <<'PY'
from pathlib import Path
import re, sys
tag = sys.argv[1]
p = Path("docker-compose.yml")
t = p.read_text()
t = re.sub(r"image:\s*lakyn80/pvm-deal-accounting-backend:\S+", f"image: lakyn80/pvm-deal-accounting-backend:{tag}", t)
p.write_text(t)
print("TAG", tag)
PY
docker compose -p pvm-deal pull accounting-backend
docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1)"
  echo "status=$st"
  [[ "$st" == "healthy" ]] && break
  [[ "$st" == "unhealthy" || "$st" == "exited" ]] && docker compose -p pvm-deal logs --tail=50 accounting-backend && exit 1
  sleep 3
done
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
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:500]}

_, login = call("POST", "http://127.0.0.1:8096/api/admin/login", body={"username": "admin", "password": password})
token = login["access_token"]
code, ares = call("GET", "http://127.0.0.1:8096/api/accounting/ares/75739593", token=token)
print("ARES", code, ares.get("company_name") if isinstance(ares, dict) else ares, ares.get("detail") if isinstance(ares, dict) else "")
code, body = call(
    "POST",
    "http://127.0.0.1:8096/api/accounting/subjects",
    token=token,
    body={
        "name": "UI Route Smoke s.r.o.",
        "email": "route@example.com",
        "address": "Praha 1",
        "ico": "22222222",
        "country": "CZ",
        "phone": None,
        "dic": None,
        "data_box": None,
        "note": None,
    },
)
print("SUBJECT", code, body.get("id") if isinstance(body, dict) else body)
html = urllib.request.urlopen("http://127.0.0.1:8096/accounting/odberatele/novy").read().decode()
print("CREATE_PAGE_OK", "assets/" in html)
PY
