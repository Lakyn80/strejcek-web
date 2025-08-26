from flask import Flask
from .config import Config
from .extensions import mail, cors
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    # init extensions
    mail.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}},
        supports_credentials=False,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Recaptcha-Token", "Authorization"],
        expose_headers=["Content-Type"],
        vary_header=True,
        always_send=True,
    )

    # blueprints
    app.register_blueprint(api_bp)

    # jednoduchý root
    @app.get("/")
    def index():
        return {"ok": True, "service": "PVM-Deal API"}

    return app
