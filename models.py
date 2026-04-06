from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class RoleType(enum.Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # In a real app, use hashed passwords
    role = db.Column(db.String(20), nullable=False, default=RoleType.VIEWER.value)
    status = db.Column(db.String(20), nullable=False, default=UserStatus.ACTIVE.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FinancialRecord(db.Model):
    __tablename__ = 'financial_records'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
