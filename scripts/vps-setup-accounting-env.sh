#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/lucky/projects/apps/pvm-deal"
TAG_FILE="$ROOT/.deploy-accounting-tag"
cd "$ROOT"

TAG="$(tr -d '[:space:]' < "$TAG_FILE")"
ACC_IMAGE="lakyn80/pvm-deal-accounting-backend:${TAG}"

if [[ ! -f .env ]] || ! grep -q '^ADMIN_PASSWORD_HASH=' .env; then
  umask 077
  if [[ ! -f .admin-password ]]; then
    openssl rand -base64 18 | tr -d '\n' > .admin-password
    chmod 600 .admin-password
  fi
  if [[ ! -f .accounting-secret-key ]]; then
    openssl rand -hex 32 | tr -d '\n' > .accounting-secret-key
    chmod 600 .accounting-secret-key
  fi

  docker pull "$ACC_IMAGE" >/dev/null
  HASH="$(docker run --rm "$ACC_IMAGE" python -m app.auth hash-password "$(cat .admin-password)")"
  SECRET_KEY="$(cat .accounting-secret-key)"

  cat > .env <<EOF
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=${HASH}
ADMIN_DISPLAY_NAME=Accounting Admin
ADMIN_EMAIL=
SECRET_KEY=${SECRET_KEY}
ADMIN_TOKEN_TTL_SECONDS=28800
ADMIN_ALLOWED_ORIGINS=https://admin.pvm-deal.cz,http://127.0.0.1:8096
APP_ENV=production
ACCOUNTING_API_PREFIX=/api/accounting
ACCOUNTING_DATABASE_URL=sqlite:////data/accounting.db
ACCOUNTING_STORAGE_PATH=/data/accounting-storage
ACCOUNTING_EMAIL_PROVIDER=console
ACCOUNTING_EMAIL_FROM=accounting@pvm-deal.cz
ACCOUNTING_ARES_PROVIDER=mock
EOF
  chmod 600 .env
  echo "ENV_CREATED"
else
  echo "ENV_EXISTS"
fi

# Never print secrets
grep -E '^[A-Z_]+=' .env | cut -d= -f1 | sort
