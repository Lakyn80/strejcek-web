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
t = re.sub(r"image:\s*lakyn80/pvm-deal-admin:\S+", f"image: lakyn80/pvm-deal-admin:{tag}", t)
t = re.sub(r"image:\s*lakyn80/pvm-deal-accounting-backend:\S+", f"image: lakyn80/pvm-deal-accounting-backend:{tag}", t)
p.write_text(t)
print("TAGS", tag)
PY
docker compose -p pvm-deal pull accounting-backend admin
docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1)"
  echo "acc=$st"
  [[ "$st" == "healthy" ]] && break
  [[ "$st" == "unhealthy" || "$st" == "exited" ]] && docker compose -p pvm-deal logs --tail=50 accounting-backend && exit 1
  sleep 3
done
docker compose -p pvm-deal up -d --force-recreate admin
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-admin-1)"
  echo "admin=$st"
  [[ "$st" == "healthy" ]] && break
  [[ "$st" == "unhealthy" || "$st" == "exited" ]] && docker compose -p pvm-deal logs --tail=50 admin && exit 1
  sleep 3
done
bash ./vps-smoke-invoice-pwa.sh
