#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
BASE=http://127.0.0.1:8096
API="$BASE/api/accounting"

PASS="$(cat .admin-password)"
LOGIN="$(curl -sf -X POST "$BASE/api/admin/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}")"
TOKEN="$(printf '%s' "$LOGIN" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"
echo "TOKEN_OK"

# UI sends X-Accounting-Demo-Token; also test Bearer.
H_BEARER=(-H "Authorization: Bearer $TOKEN")
H_UI=(-H "X-Accounting-Demo-Token: $TOKEN")

check_json() {
  local label="$1" file="$2" py="$3"
  python3 - "$file" "$label" <<'PY'
import json,sys
path,label=sys.argv[1],sys.argv[2]
d=json.load(open(path,encoding="utf-8"))
print(label, json.dumps(d, ensure_ascii=False)[:300])
PY
  python3 -c "$py" "$file"
}

echo "=== SETTINGS GET (Bearer) ==="
curl -sS -o /tmp/set.json -w "HTTP %{http_code}\n" "${H_BEARER[@]}" "$API/settings"
python3 - <<'PY'
import json
d=json.load(open("/tmp/set.json",encoding="utf-8"))
print("issuer_name=", d.get("issuer_name"), "issuer_ico=", d.get("issuer_ico"), "bank=", d.get("bank_account_number"), "/", d.get("bank_code"))
assert "issuer_name" in d, d
if not (d.get("issuer_ico") or "").strip():
    print("SETTINGS_EMPTY_WARN")
else:
    print("SETTINGS_PASS")
PY

echo "=== SETTINGS GET (UI header) ==="
curl -sS -o /tmp/set2.json -w "HTTP %{http_code}\n" "${H_UI[@]}" "$API/settings"
python3 - <<'PY'
import json
d=json.load(open("/tmp/set2.json",encoding="utf-8"))
print("ui_header issuer_ico=", d.get("issuer_ico"))
assert "issuer_name" in d
print("SETTINGS_UI_AUTH_PASS")
PY

echo "=== ARES /ares/{ico} ==="
curl -sS -o /tmp/ares.json -w "HTTP %{http_code}\n" "${H_UI[@]}" "$API/ares/75739593"
python3 - <<'PY'
import json
d=json.load(open("/tmp/ares.json",encoding="utf-8"))
print(d)
name=d.get("company_name") or d.get("name") or ""
assert "75739593" in str(d.get("ico","")) or "Robin" in name or "Strej" in name, d
print("ARES_PASS")
PY

echo "=== CREATE SUBJECT ==="
curl -sS -o /tmp/subj.json -w "HTTP %{http_code}\n" -X POST "${H_UI[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test Odberatel Audit","ico":"27074358","dic":"CZ27074358","address":"Testovaci 1, 11000 Praha","email":"test-odberatel@example.com","phone":null,"data_box":null,"country":"CZ","note":null}' \
  "$API/subjects"
python3 - <<'PY'
import json
d=json.load(open("/tmp/subj.json",encoding="utf-8"))
print(d)
assert d.get("id"), d
print("SUBJECT_CREATE_PASS id=", d["id"])
open("/tmp/subj_id.txt","w").write(str(d["id"]))
PY

echo "=== CREATE SUPPLIER ==="
curl -sS -o /tmp/sup.json -w "HTTP %{http_code}\n" -X POST "${H_UI[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test Dodavatel Audit","ico":"25596641","dic":"CZ25596641","address":"Dodavatelska 2, 60200 Brno","email":"test-dodavatel@example.com","phone":null,"data_box":null,"country":"CZ","note":null}' \
  "$API/suppliers"
python3 - <<'PY'
import json
d=json.load(open("/tmp/sup.json",encoding="utf-8"))
print(d)
assert d.get("id"), d
print("SUPPLIER_CREATE_PASS id=", d["id"])
PY

echo "=== GET SUBJECT DETAIL ==="
SID=$(cat /tmp/subj_id.txt)
curl -sS -o /tmp/subj_d.json -w "HTTP %{http_code}\n" "${H_UI[@]}" "$API/subjects/$SID"
python3 - <<'PY'
import json
d=json.load(open("/tmp/subj_d.json",encoding="utf-8"))
assert d.get("name"), d
print("SUBJECT_DETAIL_PASS", d.get("name"))
PY

echo "=== LIST SUBJECTS / SUPPLIERS ==="
curl -sS -o /tmp/slist.json -w "subjects HTTP %{http_code}\n" "${H_UI[@]}" "$API/subjects"
curl -sS -o /tmp/sulist.json -w "suppliers HTTP %{http_code}\n" "${H_UI[@]}" "$API/suppliers"
python3 - <<'PY'
import json
for path,label in [("/tmp/slist.json","subjects"),("/tmp/sulist.json","suppliers")]:
    d=json.load(open(path,encoding="utf-8"))
    items=d if isinstance(d,list) else d.get("items") or d.get("data") or []
    print(label, "count", len(items) if isinstance(items,list) else type(d), (items[:2] if isinstance(items,list) else d))
    assert isinstance(items,list) and len(items)>=1
print("LIST_PASS")
PY

echo "=== DOCUMENTS / EXPENSES / RECURRING / BANK ==="
for ep in documents expenses "recurring-templates" "bank-transactions" attachments todos settings; do
  code=$(curl -sS -o "/tmp/ep-$ep.json" -w '%{http_code}' "${H_UI[@]}" "$API/$ep")
  echo "$ep -> $code ($(head -c 80 /tmp/ep-$ep.json | tr '\n' ' '))"
done

echo "=== SEED SETTINGS IF EMPTY ==="
python3 - <<'PY'
import json,urllib.request
d=json.load(open("/tmp/set.json",encoding="utf-8"))
if (d.get("issuer_ico") or "").strip():
    print("SEED_SKIP already configured")
    raise SystemExit(0)
print("SEEDING settings from ARES snapshot")
raise SystemExit(3)
PY
SEED_RC=$?
if [[ "$SEED_RC" == "3" ]]; then
  curl -sS -o /tmp/seed.json -w "SEED HTTP %{http_code}\n" -X PUT "${H_UI[@]}" \
    -H 'Content-Type: application/json' \
    -d '{
      "owner_email":"robin.strejcek@centrum.cz",
      "issuer_name":"Robin Strejček",
      "issuer_address":"Polešovice 483",
      "issuer_city":"Polešovice",
      "issuer_zip":"68737",
      "issuer_ico":"75739593",
      "issuer_dic":"",
      "issuer_data_box":null,
      "issuer_email":"robin.strejcek@centrum.cz",
      "issuer_phone":"+420777863255",
      "default_currency":"CZK",
      "default_due_days":14,
      "default_note":null,
      "payment_method":"Převodem",
      "bank_account_number":"0000000000",
      "bank_account_prefix":null,
      "bank_code":"0100",
      "bank_iban":"",
      "account_label":""
    }' \
    "$API/settings"
  python3 - <<'PY'
import json
d=json.load(open("/tmp/seed.json",encoding="utf-8"))
print(d)
assert (d.get("issuer_ico") or "") == "75739593", d
print("SETTINGS_SEED_PASS")
PY
fi

echo "=== ADMIN SPA ROUTES ==="
for p in /accounting/ /accounting/odberatele /accounting/odberatele/novy /accounting/dodavatele /accounting/dodavatele/novy /accounting/nastaveni /accounting/doklady/novy /accounting/vydaje/novy; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE$p")
  echo "$p -> $code"
  [[ "$code" == "200" ]]
done

echo "=== ADMIN BUNDLE ==="
HTML=$(curl -sf "$BASE/accounting/")
JS=$(printf '%s' "$HTML" | grep -oE '/assets/[^" ]+\.js' | head -1)
echo "JS=$JS"
curl -sf "$BASE$JS" > /tmp/admin-bundle.js
python3 - <<'PY'
from pathlib import Path
js=Path("/tmp/admin-bundle.js").read_text(encoding="utf-8", errors="ignore")
checks={
  "odberatele": "odberatele" in js,
  "dodavatele": "dodavatele" in js,
  "novy": "/novy" in js or "novy" in js,
  "SubjectFormHint": "subjectWrite" in js or "createSubject" in js or "Odberatel" in js or "odběratel" in js.lower(),
  "pushState": "pushState" in js,
  "popstate": "popstate" in js,
}
for k,v in checks.items():
    print(f"BUNDLE_{k}={'PASS' if v else 'FAIL'}")
missing=[k for k,v in checks.items() if not v]
if missing:
    raise SystemExit(f"bundle missing: {missing}")
print("BUNDLE_PASS size", len(js))
PY

echo "=== CONTAINERS ==="
docker compose -p pvm-deal ps --format 'table {{.Name}}\t{{.Image}}\t{{.Status}}'

echo "ALL_AUDIT_PASS"
