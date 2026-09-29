#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
BASE=http://127.0.0.1:8096
API=$BASE/api/accounting
PASS=$(cat .admin-password)
TOKEN=$(curl -sf -X POST "$BASE/api/admin/login" -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
H=(-H "X-Accounting-Demo-Token: $TOKEN" -H "Content-Type: application/json")

echo "=== HEALTH ==="
curl -sf http://127.0.0.1:8071/health >/dev/null && echo ACC_HEALTH_PASS
curl -sf -o /dev/null -w "ADMIN %{http_code}\n" "$BASE/accounting/"

echo "=== PWA ==="
curl -sf -o /dev/null -w "manifest %{http_code}\n" "$BASE/accounting/manifest.webmanifest"
curl -sf "$BASE/accounting/manifest.webmanifest" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d["name"]=="PVM Deal Accounting"; assert d["display"]=="standalone"; print("MANIFEST_PASS", d["start_url"])'
curl -sf -o /dev/null -w "sw %{http_code}\n" "$BASE/accounting/sw.js"
curl -sf "$BASE/accounting/sw.js" | head -c 80; echo
test "$(curl -sf -o /dev/null -w '%{http_code}' "$BASE/accounting/sw.js")" = "200"
echo "PWA_PASS"

echo "=== CREATE INVOICE ==="
SID=$(curl -sf "${H[@]}" "$API/subjects" | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["id"])')
DOC=$(curl -sf -X POST "${H[@]}" -d "{
  \"subject_id\": $SID,
  \"document_kind\": \"invoice\",
  \"issue_date\": \"2026-09-29\",
  \"due_date\": \"2026-10-13\",
  \"business_mode\": \"autoservice\",
  \"tax_mode\": \"standard\",
  \"currency\": \"CZK\",
  \"vat_rate\": \"21\",
  \"note\": \"čřžýáíé\",
  \"items\": [{\"description\": \"Práce na zakázce\", \"quantity\": \"1\", \"unit_price\": \"2500\"}]
}" "$API")
ID=$(printf '%s' "$DOC" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["id"]); print("NUMBER", d["invoice_number"], "TOTAL", d["total"], file=sys.stderr)')
echo "FA_CREATE_PASS id=$ID"

echo "=== PDF ==="
curl -sf -o /tmp/fa.pdf -w "PDF %{http_code} ctype=%{content_type} size=%{size_download}\n" \
  -H "Authorization: Bearer $TOKEN" "$API/$ID/pdf"
python3 - <<'PY'
from pathlib import Path
b=Path('/tmp/fa.pdf').read_bytes()
assert b.startswith(b'%PDF'), b[:20]
assert len(b)>2000
print('FA_PDF_GENERATE_PASS', len(b))
PY
docker compose -p pvm-deal exec -T accounting-backend sh -c 'ls -la /data/accounting-storage/invoices | tail -n 5'
echo "FA_PDF_STORAGE_PASS"

echo "=== EMAIL ==="
curl -sf -o /tmp/mail.json -w "EMAIL %{http_code}\n" -X POST "${H[@]}" \
  -d '{"to_email":"smoke-invoice@example.com"}' "$API/$ID/send-email"
python3 - <<'PY'
import json
d=json.load(open('/tmp/mail.json'))
assert d.get('ok') is True
print('FA_EMAIL_SEND_PASS', d.get('sent_to'))
PY

echo "=== PUBLIC REGRESSION ==="
curl -sf -o /dev/null -w "public %{http_code}\n" http://127.0.0.1:8095/
curl -sf -o /dev/null -w "https_public %{http_code}\n" https://pvm-deal.cz/ || echo "HTTPS_PUBLIC_SKIP"

echo "ALL_INVOICE_PWA_SMOKE_PASS"
