from ..app import db
from datetime import datetime, timezone
import hashlib
import secrets


def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, support
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    admin = db.relationship("Admin", backref="user", uselist=False, cascade="all, delete-orphan")
    support_specialist = db.relationship("SupportSpecialist", backref="user", uselist=False, cascade="all, delete-orphan")
    business_expert = db.relationship("BusinessExpert", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set password"""
        salt = secrets.token_hex(16)
        self.password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex() + ':' + salt

    def check_password(self, password):
        """Check password"""
        try:
            hash_part, salt = self.password_hash.split(':')
            return hash_part == hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        except:
            return False

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permissions = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SupportSpecialist(db.Model):
    __tablename__ = "support_specialists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(50))
    max_applications = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'department': self.department,
            'max_applications': self.max_applications,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BusinessExpert(db.Model):
    __tablename__ = "business_experts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expertise_area = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expertise_area': self.expertise_area,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
