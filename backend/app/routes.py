from flask import Blueprint, request, jsonify, current_app
from .extensions import mail  # limiter odstraněn, zůstává jen mail (CORS se inituje v __init__.py)
from flask_mail import Message
from email_validator import validate_email, EmailNotValidError
from .emailing import build_email_bodies
from datetime import datetime
from email.utils import formataddr
import urllib.request, urllib.parse, json

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


# -----------------------
# Helpers
# -----------------------

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
    # Honeypot proti botům
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
    # reCAPTCHA je volitelná
    if not (cfg.get("ENABLE_RECAPTCHA") and cfg.get("RECAPTCHA_SECRET") and token):
        return True
    try:
        payload = urllib.parse.urlencode({
            "secret": cfg["RECAPTCHA_SECRET"],
            "response": token
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            return bool(data.get("success"))
    except Exception:
        return False


# -----------------------
# API routes
# -----------------------

# ✅ CORS preflight (OPTIONS) pro /api/contact
@api_bp.route("/contact", methods=["OPTIONS"])
def contact_options():
    # Flask-CORS doplní CORS hlavičky; 204 = No Content
    return ("", 204)


@api_bp.post("/contact")
# limiter zcela odstraněn
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

    # Konfigurace & sanity checks
    recipient_admin = current_app.config.get("MAIL_TO")
    default_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    if not recipient_admin or not default_sender:
        current_app.logger.error("MAIL_TO nebo MAIL_DEFAULT_SENDER chybí v konfiguraci.")
        return jsonify({"ok": False, "error": "Server není správně nakonfigurován (MAIL_TO/MAIL_DEFAULT_SENDER)."}), 500

    # Kontext e-mailu
    ip = _client_ip() or ""
    ua = request.headers.get("User-Agent", "")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    subject = f"Nová poptávka – {data.get('itemType', 'Neuvedeno')} – Palety/Big-Bagy/Krabice Strejček"

    # HTML + text pro admina (tvůj existující templating)
    html_body, text_body = build_email_bodies(data, ip=ip, ua=ua, when=now)

    # Reply-To nastavíme na klienta (jméno + jeho e-mail)
    reply_to_addr = formataddr((
        (data.get("name") or "").strip(),
        (data.get("email") or "").strip()
    ))

    # ---- 1) E-mail tobě (adminovi)
    admin_msg = Message(
        subject=subject,
        recipients=[recipient_admin],
        html=html_body,
        body=text_body,
        sender=default_sender,      # CENTRUM: From musí být tvoje schránka
        reply_to=reply_to_addr
    )

    try:
        mail.send(admin_msg)
    except Exception as e:
        current_app.logger.exception("Mail send to admin failed")
        # v DEBUGu vrať konkrétní chybu
        if current_app.config.get("DEBUG", False):
            return jsonify({"ok": False, "error": f"E-mail se nepodařilo odeslat: {e}"}), 500
        return jsonify({"ok": False, "error": "E-mail se nepodařilo odeslat."}), 500

    # ---- 2) Potvrzovací e-mail klientovi (plain + jednoduché HTML) — ÚPRAVENÁ PATIČKA
    client_email = (data.get("email") or "").strip()
    if _is_valid_email(client_email):
        client_subject = "Potvrzení: Vaše poptávka byla přijata"
        client_text = (
            f"Dobrý den {data.get('name')},\n\n"
            "děkujeme za Vaši poptávku. Ozveme se Vám co nejdříve.\n\n"
            "Shrnutí:\n"
            f"- Komodita: {data.get('itemType')}\n"
            f"- Množství: {data.get('quantity') or 'neuvedeno'}\n"
            f"- Lokalita: {data.get('location') or 'neuvedeno'}\n"
            f"- Zpráva: {data.get('message')}\n\n"
            "S pozdravem\n"
            "MPV-Deal Robin Strejček , Mob: +420 777 863 255"
        )
        client_html = f"""
            <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.5;color:#111">
              <p>Dobrý den {data.get('name')},</p>
              <p>děkujeme za Vaši poptávku. Ozveme se Vám co nejdříve.</p>
              <p><strong>Shrnutí</strong></p>
              <ul>
                <li><strong>Komodita:</strong> {data.get('itemType')}</li>
                <li><strong>Množství:</strong> {data.get('quantity') or 'neuvedeno'}</li>
                <li><strong>Lokalita:</strong> {data.get('location') or 'neuvedeno'}</li>
              </ul>
              <p><strong>Zpráva:</strong><br/>{(data.get('message') or '').replace(chr(10), '<br/>')}</p>
              <hr style="border:none;border-top:1px solid #ddd;margin:16px 0"/>
              <p>MPV-Deal Robin Strejček , Mob: +420 777 863 255</p>
            </div>
        """

        client_msg = Message(
            subject=client_subject,
            recipients=[client_email],
            body=client_text,
            html=client_html,
            sender=default_sender,   # From = tvoje schránka (SMTP vyžaduje)
            reply_to=formataddr(("Palety/Big-Bagy/Krabice Strejček", recipient_admin))
        )
        try:
            mail.send(client_msg)
        except Exception:
            # Nechceme blokovat úspěch jen kvůli potvrzení klientovi – zalogujeme, ale vrátíme ok.
            current_app.logger.exception("Client confirmation email failed")

    return jsonify({"ok": True, "message": "Děkujeme za zprávu, ozveme se co nejdříve."})


# -----------------------
# Test endpoint (rychlý SMTP test bez FE)
# -----------------------

@api_bp.get("/test-mail")
def test_mail():
    recipient_admin = current_app.config.get("MAIL_TO")
    default_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    if not recipient_admin or not default_sender:
        return {"ok": False, "error": "Chybí MAIL_TO nebo MAIL_DEFAULT_SENDER v konfiguraci."}, 500

    try:
        msg = Message(
            subject="Test email Strejcek-web",
            recipients=[recipient_admin],
            body="Toto je testovací email odeslaný z Flask aplikace Strejcek-web.",
            sender=default_sender
        )
        mail.send(msg)
        return {"ok": True, "message": "Test email byl odeslán."}
    except Exception as e:
        current_app.logger.exception("Test mail failed")
        return {"ok": False, "error": str(e)}, 500
