#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
PASS="${1:-}"
if [[ -z "$PASS" && -f .admin-password ]]; then
  PASS="$(cat .admin-password)"
fi
if [[ -z "$PASS" ]]; then
  echo "Usage: $0 <password>   (or keep .admin-password on server)" >&2
  exit 1
fi
python3 - "$PASS" <<'PY'
import json, sys, urllib.request
password = sys.argv[1]
req = urllib.request.Request(
    "http://127.0.0.1:8096/api/admin/login",
    data=json.dumps({"username": "admin", "password": password}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)
print("HTTP", resp.status if hasattr(resp, "status") else 200)
print("ON_SERVER_LOGIN", "YES" if data.get("access_token") else "NO")
print("USERNAME", data.get("username"))
PY
docker ps --filter name=pvm-deal-accounting-backend --format '{{.Names}} {{.Status}}'
