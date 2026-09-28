#!/usr/bin/env bash
set -euo pipefail
cd /home/lucky/projects/apps/pvm-deal
JS=$(curl -sf http://127.0.0.1:8096/accounting/ | grep -oE '/assets/[^" ]+\.js' | head -1)
curl -sf "http://127.0.0.1:8096$JS" > /tmp/admin-bundle.js
python3 - <<'PY'
from pathlib import Path
js = Path("/tmp/admin-bundle.js").read_text(encoding="utf-8", errors="ignore")
# Markers unique to deep-route AccountingApp wiring
markers = {
    "create_branch": 'type:"create"' in js or 'type:"create"' in js.replace(" ", "") or '==="create"' in js or '==="create"' in js.replace(" ",""),
    "novy_segment": '"novy"' in js or "'novy'" in js,
    "SubjectForm_mode_create": 'mode:"create"' in js or 'mode:"create"' in js.replace(" ",""),
    "odberatele_novy_href": "odberatele/novy" in js,
    "dodavatele_novy_href": "dodavatele/novy" in js,
    "pushState": "pushState" in js,
    "Accounting route not found": "Accounting route not found" in js,
}
for k,v in markers.items():
    print(f"{k}={'PASS' if v else 'FAIL'}")
# Heuristic: deep router present if create type + novy + form create mode
ok = markers["novy_segment"] and markers["odberatele_novy_href"] and markers["pushState"] and markers["Accounting route not found"]
print("DEEP_ROUTE_DEPLOYED=" + ("YES" if ok else "NO"))
if not ok:
    raise SystemExit(1)
PY
