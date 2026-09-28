#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
ACC_IMAGE="lakyn80/pvm-deal-accounting-backend:${TAG}"
NEW_PASS="${1:-${ADMIN_PASSWORD:-}}"
if [[ -z "$NEW_PASS" ]]; then
  echo "Usage: $0 <new-password>   (or set ADMIN_PASSWORD)" >&2
  exit 1
fi

umask 077
printf '%s' "$NEW_PASS" > .admin-password
chmod 600 .admin-password

HASH="$(docker run --rm "$ACC_IMAGE" python -m app.auth hash-password "$NEW_PASS")"
SECRET_KEY="$(grep '^SECRET_KEY=' accounting.env | cut -d= -f2-)"
if [[ -z "$SECRET_KEY" && -f .accounting-secret-key ]]; then
  SECRET_KEY="$(cat .accounting-secret-key)"
fi
if [[ -z "$SECRET_KEY" ]]; then
  openssl rand -hex 32 | tr -d '\n' > .accounting-secret-key
  chmod 600 .accounting-secret-key
  SECRET_KEY="$(cat .accounting-secret-key)"
fi

export RAW_HASH="$HASH"
export RAW_SECRET="$SECRET_KEY"
python3 <<'PY'
import os
from pathlib import Path
raw = os.environ["RAW_HASH"]
secret = os.environ["RAW_SECRET"]
assert raw.count("$") == 3, raw.count("$")
escaped = raw.replace("$", "$$")
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
print("ENV_UPDATED")
PY

docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend

ok=0
for i in $(seq 1 30); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1 2>/dev/null || echo missing)"
  echo "try=$i status=$st"
  if [[ "$st" == "healthy" ]]; then ok=1; break; fi
  if [[ "$st" == "unhealthy" || "$st" == "exited" || "$st" == "dead" ]]; then
    docker compose -p pvm-deal logs --tail=40 accounting-backend || true
    exit 1
  fi
  sleep 3
done
[[ "$ok" == "1" ]]

# Verify hash shape in container
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
from app.config import get_settings
h = get_settings().admin_password_hash
parts = h.split("$")
assert len(parts) == 4 and parts[0] == "pbkdf2_sha256"
print("HASH_OK")
PY

# Login via admin proxy
RESP="$(curl -sf -X POST http://127.0.0.1:8096/api/admin/login \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$NEW_PASS\"}")"
python3 -c 'import json,sys; d=json.loads(sys.argv[1]); assert d.get("access_token"); print("LOGIN_OK", d.get("username"))' "$RESP"
