#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
ACC="lakyn80/pvm-deal-accounting-backend:${TAG}"
echo "Deploying $ACC"

# Point compose image to new tag if compose uses variable/file
if grep -q 'pvm-deal-accounting-backend:' docker-compose.yml; then
  python3 - "$TAG" <<'PY'
from pathlib import Path
import re, sys
tag = sys.argv[1]
path = Path("docker-compose.yml")
text = path.read_text(encoding="utf-8")
new = re.sub(
    r"(image:\s*lakyn80/pvm-deal-accounting-backend:)[^\s]+",
    rf"\g<1>{tag}",
    text,
)
path.write_text(new, encoding="utf-8")
print("compose image retagged")
PY
fi

docker pull "$ACC"
docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend

ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "try=$i status=$st"
  if [[ "$st" == "healthy" || "$st" == "running" ]]; then
    if curl -sf http://127.0.0.1:8071/health >/dev/null; then
      ok=1
      break
    fi
  fi
  sleep 2
done
[[ "$ok" == "1" ]] || { docker compose -p pvm-deal logs --tail=80 accounting-backend; exit 1; }
echo HEALTH_OK
