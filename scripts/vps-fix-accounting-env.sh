#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
ACC_IMAGE="lakyn80/pvm-deal-accounting-backend:${TAG}"

umask 077
if [[ ! -f .admin-password ]]; then
  openssl rand -base64 18 | tr -d '\n' > .admin-password
  chmod 600 .admin-password
fi
if [[ ! -f .accounting-secret-key ]]; then
  openssl rand -hex 32 | tr -d '\n' > .accounting-secret-key
  chmod 600 .accounting-secret-key
fi

PASS="$(cat .admin-password)"
HASH="$(docker run --rm "$ACC_IMAGE" python -m app.auth hash-password "$PASS")"
SECRET_KEY="$(cat .accounting-secret-key)"

python3 - "$HASH" "$SECRET_KEY" <<'PY'
import sys
from pathlib import Path
hash_value = sys.argv[1]
secret = sys.argv[2]
content = (
    "ADMIN_USERNAME=admin\n"
    f"ADMIN_PASSWORD_HASH={hash_value}\n"
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
parts = hash_value.split("$")
assert parts[0] == "pbkdf2_sha256", parts[0]
assert parts[1].isdigit(), parts[1]
assert len(parts) == 4
print("HASH_OK", "algo", parts[0], "iters", parts[1], "parts", len(parts))
PY

rm -f .env
python3 - <<'PY'
from pathlib import Path
p = Path("docker-compose.yml")
t = p.read_text()
t = t.replace("- ./.env", "- ./accounting.env")
p.write_text(t)
print("COMPOSE_ENV_FILE_OK")
PY

docker compose -p pvm-deal config > /tmp/pvm-compose-config.yml
python3 - <<'PY'
import re
cfg = open("/tmp/pvm-compose-config.yml").read()
m = re.search(r"ADMIN_PASSWORD_HASH:\s*([^\n]+)", cfg)
val = m.group(1).strip().strip('"') if m else ""
parts = val.split("$")
print("CONFIG_HASH_PARTS", len(parts), "algo", parts[0] if parts else None)
print("CONFIG_HASH_OK", len(parts) == 4 and parts[0] == "pbkdf2_sha256")
if not (len(parts) == 4 and parts[0] == "pbkdf2_sha256"):
    raise SystemExit(1)
PY
