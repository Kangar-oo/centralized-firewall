# db.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Log table for firewall events
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(100))
    details = db.Column(db.Text)
    timestamp = db.Column(db.String(50))
