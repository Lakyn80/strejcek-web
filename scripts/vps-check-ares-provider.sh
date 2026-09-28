#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
docker compose -p pvm-deal exec -T accounting-backend python - <<'PY'
import os
from accounting_api.integrations.ares.provider import resolve_ares_provider
r = resolve_ares_provider()
print("env", os.getenv("ACCOUNTING_ARES_PROVIDER"))
print("mode", r.mode)
print("provider", type(r.provider).__name__)
print("module_file", getattr(type(r.provider), "__module__", None))
PY
