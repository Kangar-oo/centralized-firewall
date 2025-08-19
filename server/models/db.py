import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)
    
    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Rule(db.Model):
    __tablename__ = 'rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    source_ip = db.Column(db.String(50))
    source_port = db.Column(db.String(10))
    destination_ip = db.Column(db.String(50))
    destination_port = db.Column(db.String(10))
    protocol = db.Column(db.String(10))  # tcp, udp, icmp, any
    action = db.Column(db.String(10), nullable=False)  # ALLOW, DENY
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    creator = db.relationship('User', backref='rules')

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # FIREWALL, AUTH, SYSTEM
    level = db.Column(db.String(10))  # INFO, WARNING, ERROR, CRITICAL
    source_ip = db.Column(db.String(50))
    destination_ip = db.Column(db.String(50))
    action = db.Column(db.String(20))  # ALLOW, DENY, LOGIN, LOGOUT, etc.
    details = db.Column(db.Text)
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    rule = db.relationship('Rule', backref='logs')
    user = db.relationship('User', backref='logs')

def init_db(app):
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if not exists
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD_HASH')
        
        if not User.query.filter_by(username=admin_username).first():
            admin = User(
                username=admin_username,
                is_admin=True
            )
            admin.password_hash = admin_password
            db.session.add(admin)
            db.session.commit()
