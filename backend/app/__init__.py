from flask import Flask
from .config import Config
from .extensions import mail, cors
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    mail.init_app(app)

    # ✅ Robustní CORS: povolí jakýkoli origin (dočasně), metody a hlavičky pro preflight
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Recaptcha-Token", "Authorization"],
        expose_headers=["Content-Type"],
        vary_header=True,
        always_send=True,       # pošli CORS i na 4xx/5xx
        send_wildcard=True      # Access-Control-Allow-Origin: *
    )

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return {"ok": True, "service": "Palety • Big-Bagy • Krabice Strejček API"}

    return app
