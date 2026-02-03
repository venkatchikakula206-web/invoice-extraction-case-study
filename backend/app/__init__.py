from flask import Flask
from flask_cors import CORS
from .config import Settings
from .db import init_db
from .routes import api
from .seed import maybe_seed_from_excel

def create_app() -> Flask:
    settings = Settings.from_env()
    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure directories + DB
    init_db(settings)

    # Seed from Excel if present (idempotent)
    maybe_seed_from_excel(app)

    # API routes
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
