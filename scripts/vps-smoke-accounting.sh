#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

echo "=== 8071 HEALTH ==="
curl -sf http://127.0.0.1:8071/health
echo
echo "ACCOUNTING_HEALTH_PASS"

echo "=== 8096 ADMIN GET ==="
curl -sf http://127.0.0.1:8096/accounting/ >/dev/null
echo "ADMIN_LOCALHOST_PASS"

echo "=== LOGIN VIA ADMIN PROXY ==="
PASS="$(cat .admin-password)"
RESP="$(curl -sf -X POST http://127.0.0.1:8096/api/admin/login \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}")"
python3 - "$RESP" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
assert data.get("access_token"), data
assert data.get("token_type") == "bearer"
print("LOGIN_PROXY_PASS username=", data.get("username"))
PY

echo "=== 8095 PUBLIC FRONTEND ==="
curl -sf -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/
echo "FRONTEND_LOCAL_PASS"

echo "=== HTTPS pvm-deal.cz ==="
curl -sf -o /dev/null -w "%{http_code}\n" https://pvm-deal.cz/
echo "PUBLIC_PVM_DEAL_PASS"

echo "=== PERSISTENCE ==="
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from pathlib import Path
p = Path("/data/accounting.db")
print("DB_EXISTS_BEFORE", p.exists(), "SIZE", p.stat().st_size if p.exists() else 0)
PY
# Create marker inside volume
docker compose -p pvm-deal exec -T accounting-backend sh -c 'echo persist-ok > /data/persist-marker.txt'
BEFORE="$(docker compose -p pvm-deal exec -T accounting-backend cat /data/persist-marker.txt | tr -d '\r\n')"
echo "MARKER_BEFORE=$BEFORE"
docker compose -p pvm-deal restart accounting-backend
ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "restart try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  sleep 3
done
[[ "$ok" == "1" ]]
AFTER="$(docker compose -p pvm-deal exec -T accounting-backend cat /data/persist-marker.txt | tr -d '\r\n')"
echo "MARKER_AFTER=$AFTER"
[[ "$AFTER" == "persist-ok" ]]
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from pathlib import Path
p = Path("/data/accounting.db")
print("DB_EXISTS_AFTER", p.exists(), "SIZE", p.stat().st_size if p.exists() else 0)
assert p.exists() and p.stat().st_size > 0
PY
echo "PERSISTENCE_PASS"

echo "=== CONTAINERS ==="
docker ps --filter name=pvm-deal --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

echo "=== PORTS ==="
ss -lnt | grep -E ':(8070|8071|8095|8096)\s' || true

echo "=== BE/FE UNCHANGED CHECK ==="
docker inspect pvm-deal-backend-1 --format '{{.Image}} {{.State.StartedAt}}'
docker inspect pvm-deal-frontend-1 --format '{{.Image}} {{.State.StartedAt}}'

echo "ALL_SMOKE_PASS"
