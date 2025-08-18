# App.py

from flask import Flask
from routes.logs import logs_bp
from routes.rules import rules_bp
from routes.auth import auth_bp
from models.db import db

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///firewall.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------------------

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# -------------------------------

# Register API blueprints
app.register_blueprint(logs_bp, url_prefix='/logs')
app.register_blueprint(rules_bp, url_prefix='/rules')
app.register_blueprint(auth_bp, url_prefix='/auth')

# -------------------------------

# Root endpoint for API health check
@app.route("/", methods=["GET"])
def root():
    return {"status": "success", "message": "Centralized Firewall API is running"}, 200

# -------------------------------

# Run the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
