# logs.py

from flask import Blueprint, request, jsonify
from services import log_service
from services import security_service

logs_bp = Blueprint('logs', __name__)

# POST logs from Go agent
@logs_bp.route("/", methods=["POST"])
def receive_log():
    # Optional: validate request
    if not security_service.validate_request(request):
        return jsonify({"status": "failed", "reason": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"status": "failed", "reason": "No JSON received"}), 400

    # Use log_service to save log
    log_entry = log_service.add_log(
        event=data.get("event", "unknown"),
        details=data.get("details", ""),
        timestamp=data.get("time", security_service.get_current_time())
    )
    return jsonify({"status": "success"}), 200

# GET all logs
@logs_bp.route("/", methods=["GET"])
def get_logs():
    logs = log_service.get_all_logs()
    return jsonify(logs), 200
