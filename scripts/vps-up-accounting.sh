#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

echo "=== PULL ==="
docker compose -p pvm-deal pull accounting-backend admin

echo "=== UP accounting-backend ==="
docker compose -p pvm-deal up -d --no-deps accounting-backend

echo "=== WAIT HEALTH ==="
ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then
    ok=1
    break
  fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" || "$st" == "dead" ]]; then
    docker compose -p pvm-deal logs --tail=80 accounting-backend || true
    exit 1
  fi
  sleep 3
done
if [[ "$ok" != "1" ]]; then
  docker compose -p pvm-deal logs --tail=80 accounting-backend || true
  exit 1
fi

echo "=== HEALTH CURL ==="
curl -sf http://127.0.0.1:8071/health
echo

echo "=== HASH IN CONTAINER ==="
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from app.config import get_settings
h = get_settings().admin_password_hash
parts = h.split("$")
print("IN_CONTAINER_PARTS", len(parts), "algo", parts[0] if parts else None, "iters", parts[1] if len(parts) > 1 else None)
print("IN_CONTAINER_HASH_OK", len(parts) == 4 and parts[0] == "pbkdf2_sha256")
if not (len(parts) == 4 and parts[0] == "pbkdf2_sha256"):
    raise SystemExit(2)
PY

echo "=== UP admin ==="
docker compose -p pvm-deal up -d admin

ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-admin-1 2>/dev/null || echo missing)"
  echo "admin try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then
    ok=1
    break
  fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" || "$st" == "dead" ]]; then
    docker compose -p pvm-deal logs --tail=80 admin || true
    exit 1
  fi
  sleep 3
done
if [[ "$ok" != "1" ]]; then
  docker compose -p pvm-deal logs --tail=80 admin || true
  exit 1
fi

echo "DEPLOY_SERVICES_OK"
