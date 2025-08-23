# server/routes/agent_auth.py

from flask import Blueprint, request, jsonify
import sqlite3
import hashlib
from flask_jwt_extended import create_access_token

# Blueprint mounted at: /api/v1/agent
agent_auth_bp = Blueprint("agent_auth", __name__)

DB_PATH = "server/firewall.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_secret(secret: str) -> str:
    """Hash agent secrets (replace with bcrypt/argon2 in production)."""
    return hashlib.sha256(secret.encode()).hexdigest()


# 🔹 Create table if not exists
def init_agent_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT UNIQUE NOT NULL,
            agent_secret TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# 🔹 Register new agent
@agent_auth_bp.route("/register", methods=["POST"])
def register_agent():
    data = request.get_json(silent=True) or {}
    agent_id = data.get("agent_id")
    agent_secret = data.get("agent_secret")

    if not agent_id or not agent_secret:
        return jsonify({"status": "error", "message": "Missing agent_id or agent_secret"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO agents (agent_id, agent_secret) VALUES (?, ?)",
            (agent_id, hash_secret(agent_secret)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "Agent already exists"}), 409

    conn.close()
    return jsonify({"status": "success", "message": f"Agent {agent_id} registered"}), 201


# 🔹 Agent login with JWT token
@agent_auth_bp.route("/login", methods=["POST"])
def agent_login():
    data = request.get_json(silent=True) or {}
    agent_id = data.get("agent_id")
    agent_secret = data.get("agent_secret")

    if not agent_id or not agent_secret:
        return jsonify({"status": "error", "message": "Missing agent_id or agent_secret"}), 400

    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM agents WHERE agent_id = ?", (agent_id,)
    ).fetchone()
    conn.close()

    if row and row["agent_secret"] == hash_secret(agent_secret):
        # Generate JWT token
        access_token = create_access_token(identity=agent_id)
        return jsonify({
            "status": "success",
            "message": "Agent authenticated",
            "agent_id": agent_id,
            "access_token": access_token
        }), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# Ensure table exists on import
init_agent_table()
