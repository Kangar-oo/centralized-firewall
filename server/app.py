# App.py

from flask import Flask, render_template
from routes.logs import logs_bp
from routes.rules import rules_bp
from routes.auth import auth_bp
from services import log_service, rule_service
from models.db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///firewall.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Register API blueprints
app.register_blueprint(logs_bp, url_prefix='/logs')
app.register_blueprint(rules_bp, url_prefix='/rules')
app.register_blueprint(auth_bp, url_prefix='/auth')

# -------------------------------
# Dashboard Pages
# -------------------------------

@app.route("/")
def home():
    """Dashboard homepage"""
    return render_template("index.html")

@app.route("/logs_page")
def logs_page():
    """Display firewall logs"""
    logs = log_service.get_all_logs()
    return render_template("logs.html", logs=logs)

@app.route("/rules_page")
def rules_page():
    """Display firewall rules"""
    rules = rule_service.get_rules()
    return render_template("rules.html", rules=rules)

# Run the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)