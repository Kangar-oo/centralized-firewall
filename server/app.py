from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from server.routes.logs import logs_bp
from server.routes.rules import rules_bp
from server.routes.auth import auth_bp
from server.models.db import db


def create_app():
    app = Flask(__name__)

    # -------------------------------
    # Database Config
    # -------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///firewall.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------------------
    # JWT Config
    # -------------------------------
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change in production
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_COOKIE_SECURE"] = False  # True if HTTPS
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # -------------------------------
    # Init Extensions
    # -------------------------------
    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt = JWTManager(app)

    # Create tables if not exist
    with app.app_context():
        db.create_all()

    # -------------------------------
    # Register Blueprints
    # -------------------------------
    app.register_blueprint(logs_bp, url_prefix="/logs")
    app.register_blueprint(rules_bp, url_prefix="/rules")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # -------------------------------
    # Root endpoint for API health check
    # -------------------------------
    @app.route("/", methods=["GET"])
    def root():
        return {"status": "success", "message": "Centralized Firewall API is running"}, 200

    return app


# -------------------------------
# Run the Flask server
# -------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000, 
        debug=True
        )
