# rules.py

from flask import Blueprint, request, jsonify
from services import rule_service
from services import security_service

rules_bp = Blueprint('rules', __name__)

# GET all rules
@rules_bp.route("/", methods=["GET"])
def get_rules():
    return jsonify(rule_service.get_rules()), 200

# POST a new rule
@rules_bp.route("/", methods=["POST"])
def add_rule():
    # Optional: validate request
    if not security_service.validate_request(request):
        return jsonify({"status": "failed", "reason": "Unauthorized"}), 401

    data = request.json
    if not data or "type" not in data or "target" not in data:
        return jsonify({"status": "failed", "reason": "Invalid rule format"}), 400

    rule = rule_service.add_rule(data["type"], data["target"])
    return jsonify({"status": "rule added", "rule": rule}), 200
