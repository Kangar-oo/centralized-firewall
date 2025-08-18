# auth.py

from flask import Blueprint, request, jsonify
from services import security_service

auth_bp = Blueprint('auth', __name__)

# POST /auth/login → simple login endpoint
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"status": "failed", "reason": "Invalid credentials"}), 400

    username = data.get("username")
    password = data.get("password")

    # Dummy authentication logic
    if username == "admin" and password == "admin123":
        # Optionally, generate token or API key
        api_key = "SECRET123"
        return jsonify({"status": "success", "api_key": api_key}), 200

    return jsonify({"status": "failed", "reason": "Unauthorized"}), 401

# Example: API key verification endpoint
@auth_bp.route("/validate", methods=["POST"])
def validate():
    if security_service.validate_request(request):
        return jsonify({"status": "success", "message": "Valid API key"}), 200
    return jsonify({"status": "failed", "message": "Invalid API key"}), 401
