from flask import Blueprint, request, jsonify, current_app
from .extensions import limiter, mail
from flask_mail import Message
from email_validator import validate_email, EmailNotValidError
from .emailing import build_email_bodies
from datetime import datetime
import urllib.request, urllib.parse, json

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

def _is_valid_email(addr: str) -> bool:
    try:
        validate_email(addr, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def _validate_payload(data: dict) -> tuple[bool, str]:
    required = ["name", "email", "itemType", "message"]
    for field in required:
        if not data.get(field):
            return False, f"Pole '{field}' je povinné."
    if len(data.get("name", "")) > 100:
        return False, "Jméno je příliš dlouhé."
    if not _is_valid_email(data.get("email", "")):
        return False, "E-mail není platný."
    if len(data.get("message", "")) > 5000:
        return False, "Zpráva je příliš dlouhá."
    if data.get("company"):
        return False, "Spam zablokován."
    return True, ""

def _client_ip():
    xfwd = request.headers.get("X-Forwarded-For", "")
    if xfwd:
        return xfwd.split(",")[0].strip()
    return request.remote_addr

def _verify_recaptcha(token: str) -> bool:
    cfg = current_app.config
    if not (cfg.get("ENABLE_RECAPTCHA") and cfg.get("RECAPTCHA_SECRET") and token):
        return True
    try:
        payload = urllib.parse.urlencode({
            "secret": cfg["RECAPTCHA_SECRET"],
            "response": token
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            return bool(data.get("success"))
    except Exception:
        return False

@api_bp.post("/contact")
@limiter.limit(lambda: current_app.config.get("RATE_LIMIT", "5 per minute"))
def contact():
    if not request.is_json:
        return jsonify({"ok": False, "error": "Očekáván JSON payload."}), 400
    data = request.get_json() or {}
    ok, msg = _validate_payload(data)
    if not ok:
        return jsonify({"ok": False, "error": msg}), 400

    token = data.get("captchaToken") or request.headers.get("X-Recaptcha-Token", "")
    if not _verify_recaptcha(token):
        return jsonify({"ok": False, "error": "Neplatná reCAPTCHA."}), 400

    ip = _client_ip() or ""
    ua = request.headers.get("User-Agent", "")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    subject = f"Nová poptávka – {data.get('itemType', 'Neuvedeno')} – Palety/Big-Bagy/Krabice Strejček"
    html_body, text_body = build_email_bodies(data, ip=ip, ua=ua, when=now)

    msg = Message(subject=subject,
                  recipients=[current_app.config["MAIL_TO"]],
                  html=html_body,
                  body=text_body)
    try:
        mail.send(msg)
    except Exception:
        return jsonify({"ok": False, "error": "E-mail se nepodařilo odeslat."}), 500

    return jsonify({"ok": True, "message": "Děkujeme za zprávu, ozveme se co nejdříve."})
