#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
ACC_IMAGE="lakyn80/pvm-deal-accounting-backend:${TAG}"

umask 077
PASS="$(cat .admin-password)"
HASH="$(docker run --rm "$ACC_IMAGE" python -m app.auth hash-password "$PASS")"
SECRET_KEY="$(cat .accounting-secret-key)"

# Pass raw hash via env; Python doubles dollars for Compose
export RAW_HASH="$HASH"
export RAW_SECRET="$SECRET_KEY"
python3 <<'PY'
import os
from pathlib import Path
raw = os.environ["RAW_HASH"]
secret = os.environ["RAW_SECRET"]
assert raw.count("$") == 3, raw.count("$")
escaped = raw.replace("$", "$$")
assert escaped.count("$$") == 3
content = (
    "ADMIN_USERNAME=admin\n"
    f"ADMIN_PASSWORD_HASH={escaped}\n"
    "ADMIN_DISPLAY_NAME=Accounting Admin\n"
    "ADMIN_EMAIL=\n"
    f"SECRET_KEY={secret}\n"
    "ADMIN_TOKEN_TTL_SECONDS=28800\n"
    "ADMIN_ALLOWED_ORIGINS=https://admin.pvm-deal.cz,http://127.0.0.1:8096\n"
    "APP_ENV=production\n"
    "ACCOUNTING_API_PREFIX=/api/accounting\n"
    "ACCOUNTING_DATABASE_URL=sqlite:////data/accounting.db\n"
    "ACCOUNTING_STORAGE_PATH=/data/accounting-storage\n"
    "ACCOUNTING_EMAIL_PROVIDER=console\n"
    "ACCOUNTING_EMAIL_FROM=accounting@pvm-deal.cz\n"
    "ACCOUNTING_ARES_PROVIDER=mock\n"
)
Path("accounting.env").write_text(content)
Path("accounting.env").chmod(0o600)
# Verify file on disk has doubled dollars (read without shell)
file_hash = [l for l in Path("accounting.env").read_text().splitlines() if l.startswith("ADMIN_PASSWORD_HASH=")][0].split("=",1)[1]
print("FILE_DOUBLE_DOLLAR_COUNT", file_hash.count("$$"))
print("FILE_SINGLE_ORPHAN_CHECK", file_hash.replace("$$", "").count("$"))
PY

docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend

ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" || "$st" == "dead" ]]; then
    docker compose -p pvm-deal logs --tail=50 accounting-backend || true
    exit 1
  fi
  sleep 3
done
[[ "$ok" == "1" ]]

docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from app.config import get_settings
h = get_settings().admin_password_hash
parts = h.split("$")
print("IN_CONTAINER_PARTS", len(parts), "algo", parts[0], "iters", parts[1] if len(parts) > 1 else None)
assert len(parts) == 4 and parts[0] == "pbkdf2_sha256" and parts[1] == "600000"
print("HASH_IN_CONTAINER_OK")
PY

docker compose -p pvm-deal up -d admin
ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-admin-1 2>/dev/null || echo missing)"
  echo "admin try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" || "$st" == "dead" ]]; then
    docker compose -p pvm-deal logs --tail=50 admin || true
    exit 1
  fi
  sleep 3
done
[[ "$ok" == "1" ]]
echo "SERVICES_READY"
