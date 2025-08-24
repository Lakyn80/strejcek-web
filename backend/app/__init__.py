from flask import Flask
from .config import Config
from .extensions import mail, cors, limiter
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    mail.init_app(app)

    allowed = [o.strip() for o in app.config.get("ALLOWED_ORIGINS", [])]
    cors.init_app(app, resources={r"/api/*": {"origins": allowed}}, supports_credentials=False)

    limiter.init_app(app)

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return {"ok": True, "service": "Palety • Big-Bagy • Krabice Strejček API"}

    return app
