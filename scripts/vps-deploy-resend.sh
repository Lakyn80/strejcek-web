#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal

# Merge Resend settings into accounting.env without printing secrets.
python3 - <<'PY'
from pathlib import Path
p = Path("accounting.env")
lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
wanted = {
    "ACCOUNTING_EMAIL_PROVIDER": "resend",
    "ACCOUNTING_EMAIL_FROM": "faktury@pvm-deal.cz",
    "RESEND_FROM_EMAIL": "faktury@pvm-deal.cz",
    "RESEND_FROM_NAME": "PVM Deal",
    "ACCOUNTING_INVOICE_COPY_EMAIL": "robin.strejcek@centrum.cz",
}
# RESEND_API_KEY comes from uploaded .resend-api-key file if present
key_file = Path(".resend-api-key")
if key_file.exists():
    key = key_file.read_text(encoding="utf-8").strip()
    if key:
        wanted["RESEND_API_KEY"] = key
    key_file.unlink(missing_ok=True)

keys = set()
out = []
for line in lines:
    if not line or line.startswith("#") or "=" not in line:
        out.append(line)
        continue
    k, _, v = line.partition("=")
    if k in wanted:
        out.append(f"{k}={wanted[k]}")
        keys.add(k)
    else:
        out.append(line)
for k, v in wanted.items():
    if k not in keys:
        out.append(f"{k}={v}")
p.write_text("\n".join(out) + "\n", encoding="utf-8")
p.chmod(0o600)
print("ENV_UPDATED keys=", sorted(wanted.keys()))
PY

TAG="$(tr -d '[:space:]' < .deploy-accounting-tag)"
python3 - "$TAG" <<'PY'
from pathlib import Path
import re, sys
tag = sys.argv[1]
p = Path("docker-compose.yml")
t = p.read_text()
t = re.sub(r"image:\s*lakyn80/pvm-deal-accounting-backend:\S+", f"image: lakyn80/pvm-deal-accounting-backend:{tag}", t)
# Ensure compose environment uses resend provider if hardcoded console remains
t = t.replace('ACCOUNTING_EMAIL_PROVIDER: "console"', 'ACCOUNTING_EMAIL_PROVIDER: "resend"')
t = t.replace("ACCOUNTING_EMAIL_FROM: \"accounting@pvm-deal.cz\"", 'ACCOUNTING_EMAIL_FROM: "faktury@pvm-deal.cz"')
if "RESEND_FROM_EMAIL" not in t:
    t = t.replace(
        'ACCOUNTING_EMAIL_PROVIDER: "resend"',
        'ACCOUNTING_EMAIL_PROVIDER: "resend"\n      RESEND_FROM_EMAIL: "faktury@pvm-deal.cz"\n      RESEND_FROM_NAME: "PVM Deal"\n      ACCOUNTING_INVOICE_COPY_EMAIL: "robin.strejcek@centrum.cz"',
        1,
    )
p.write_text(t)
print("COMPOSE_TAG", tag)
PY

docker compose -p pvm-deal pull accounting-backend
docker compose -p pvm-deal up -d --no-deps --force-recreate accounting-backend
for i in $(seq 1 40); do
  st="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pvm-deal-accounting-backend-1)"
  echo "status=$st"
  [[ "$st" == "healthy" ]] && break
  [[ "$st" == "unhealthy" || "$st" == "exited" ]] && docker compose -p pvm-deal logs --tail=80 accounting-backend && exit 1
  sleep 3
done

# Verify env loaded (never print API key value)
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
import os
print("provider", os.getenv("ACCOUNTING_EMAIL_PROVIDER"))
print("from", os.getenv("RESEND_FROM_EMAIL"))
print("name", os.getenv("RESEND_FROM_NAME"))
print("copy", os.getenv("ACCOUNTING_INVOICE_COPY_EMAIL"))
print("key_set", "yes" if (os.getenv("RESEND_API_KEY") or "").strip() else "no")
PY

echo DEPLOY_RESEND_OK
