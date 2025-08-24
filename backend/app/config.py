import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # CORS
    _origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    ALLOWED_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "25"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME or "no-reply@example.com")
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "False").lower() == "true"
    MAIL_TO = os.getenv("MAIL_TO", MAIL_USERNAME or "owner@example.com")

    # Limiter
    RATE_LIMIT = os.getenv("RATE_LIMIT", "5 per minute")

    # reCAPTCHA
    ENABLE_RECAPTCHA = os.getenv("ENABLE_RECAPTCHA", "False").lower() == "true"
    RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET", "")
