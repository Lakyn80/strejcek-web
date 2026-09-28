#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
BASE=http://127.0.0.1:8096
API=$BASE/api/accounting
PASS=$(cat .admin-password)
TOKEN=$(curl -sf -X POST "$BASE/api/admin/login" -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
H=(-H "X-Accounting-Demo-Token: $TOKEN" -H "Content-Type: application/json")

echo "=== LIST INVOICES ==="
curl -sS -L -o /tmp/inv.json -w "HTTP %{http_code}\n" "${H[@]}" "$API"
python3 - <<'PY'
import json
d=json.load(open("/tmp/inv.json",encoding="utf-8"))
assert isinstance(d,list), d
print("invoices", len(d), "LIST_PASS")
PY

SID=$(curl -sf "${H[@]}" "$API/subjects" | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["id"])')
echo "subject_id=$SID"

echo "=== CREATE DOCUMENT ==="
curl -sS -o /tmp/doc.json -w "HTTP %{http_code}\n" -X POST "${H[@]}" -d "{
  \"subject_id\": $SID,
  \"document_kind\": \"invoice\",
  \"issue_date\": \"2026-09-28\",
  \"due_date\": \"2026-10-12\",
  \"business_mode\": \"autoservice\",
  \"tax_mode\": \"standard\",
  \"currency\": \"CZK\",
  \"vat_rate\": \"21\",
  \"items\": [{\"description\": \"Audit polozka\", \"quantity\": \"1\", \"unit_price\": \"1000\"}]
}" "$API"
python3 - <<'PY'
import json
d=json.load(open("/tmp/doc.json",encoding="utf-8"))
print(str(d)[:600])
assert d.get("id"), d
print("DOCUMENT_CREATE_PASS", d["id"])
PY

echo "DOC_AUDIT_PASS"
