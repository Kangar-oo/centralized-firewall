# security_service.py

# server/services/security_service.py

from functools import wraps
from flask import request, jsonify, g
from server.models.db import db, Log, User

# -------------------------

# Admin Access Decorator

# -------------------------
def admin_required(f):
    """
    Flask decorator to restrict routes to admin users only.
    It checks the Authorization header or user role in context.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        # Example: Token = "Bearer <username>"
        try:
            token = auth_header.split(" ")[1]
            user = User.query.filter_by(username=token).first()
        except Exception:
            return jsonify({"error": "Invalid token format"}), 401

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # Store current user in Flask global context
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


# -------------------------
# Activity Logging
# -------------------------
def log_activity(user, action, details=None):
    """
    Logs user activity into the database.
    """
    log = Log(user_id=user.id if user else None,
              action=action,
              details=details)

    db.session.add(log)
    db.session.commit()

    print(f"[SECURITY LOG] User={user.username if user else 'Unknown'}, "
          f"Action={action}, Details={details}")
