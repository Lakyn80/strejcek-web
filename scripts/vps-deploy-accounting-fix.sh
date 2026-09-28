#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
ACC="lakyn80/pvm-deal-accounting-backend:${TAG}"
ADM="lakyn80/pvm-deal-admin:${TAG}"

python3 - "$ACC" "$ADM" <<'PY'
from pathlib import Path
import sys
acc, adm = sys.argv[1], sys.argv[2]
path = Path("docker-compose.yml")
text = path.read_text()
import re
text = re.sub(
    r"image:\s*lakyn80/pvm-deal-accounting-backend:\S+",
    f"image: {acc}",
    text,
)
text = re.sub(
    r"image:\s*lakyn80/pvm-deal-admin:\S+",
    f"image: {adm}",
    text,
)
text = text.replace('ACCOUNTING_ARES_PROVIDER: "mock"', 'ACCOUNTING_ARES_PROVIDER: "real"')
text = text.replace("ACCOUNTING_ARES_PROVIDER: mock", 'ACCOUNTING_ARES_PROVIDER: "real"')
path.write_text(text)
print("COMPOSE_UPDATED")
print([line for line in text.splitlines() if "image: lakyn80/pvm-deal-" in line or "ARES" in line])
PY

# Keep ARES real in accounting.env if present
if [[ -f accounting.env ]]; then
  python3 <<'PY'
from pathlib import Path
p = Path("accounting.env")
lines = []
found = False
for line in p.read_text().splitlines():
    if line.startswith("ACCOUNTING_ARES_PROVIDER="):
        lines.append("ACCOUNTING_ARES_PROVIDER=real")
        found = True
    else:
        lines.append(line)
if not found:
    lines.append("ACCOUNTING_ARES_PROVIDER=real")
p.write_text("\n".join(lines) + "\n")
print("ENV_ARES_REAL")
PY
fi

docker compose -p pvm-deal pull accounting-backend admin
docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend
ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "acc try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" ]]; then docker compose -p pvm-deal logs --tail=40 accounting-backend; exit 1; fi
  sleep 3
done
[[ "$ok" == "1" ]]
docker compose -p pvm-deal up -d --force-recreate admin
ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-admin-1 2>/dev/null || echo missing)"
  echo "admin try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" ]]; then docker compose -p pvm-deal logs --tail=40 admin; exit 1; fi
  sleep 3
done
[[ "$ok" == "1" ]]

PASS="$(cat .admin-password)"
python3 - "$PASS" <<'PY'
import json, sys, urllib.request, urllib.error
password=sys.argv[1]

def call(method, url, token=None, body=None):
    data=None if body is None else json.dumps(body).encode()
    headers={"Content-Type":"application/json"}
    if token:
        headers["Authorization"]=f"Bearer {token}"
        headers["X-Accounting-Demo-Token"]=token
    req=urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw=resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw=e.read().decode()
        try: payload=json.loads(raw)
        except Exception: payload={"raw":raw[:300]}
        return e.code, payload

_, login=call("POST","http://127.0.0.1:8096/api/admin/login", body={"username":"admin","password":password})
token=login["access_token"]
print("LOGIN_OK")
code, settings=call("GET","http://127.0.0.1:8096/api/accounting/settings", token=token)
print("SETTINGS", code, settings.get("issuer_ico"))
code, ares=call("GET","http://127.0.0.1:8096/api/accounting/ares/75739593", token=token)
print("ARES_REAL", code, ares.get("company_name") if isinstance(ares, dict) else ares)
code, page=call("GET","http://127.0.0.1:8096/accounting/odberatele/novy")
# GET html may not be json
print("CREATE_PAGE_HTTP", code)
code, body=call("POST","http://127.0.0.1:8096/api/accounting/subjects", token=token, body={
  "name":"Smoke Odběratel a.s.",
  "email":"smoke2@example.com",
  "address":"Ulice 5, 11000 Praha",
  "ico":"11111111",
  "dic":None,
  "data_box":None,
  "country":"CZ",
  "phone":None,
  "note":None,
})
print("CREATE_SUBJECT", code, body.get("id") if isinstance(body, dict) else body)
PY
echo DEPLOY_FIX_OK
