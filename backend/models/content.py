from ..app import db
from datetime import datetime, timezone

def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)

class ContentManagement(db.Model):
    __tablename__ = "content_management"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_type = db.Column(db.String(50), nullable=False)  # about, contact
    section_key = db.Column(db.String(100), nullable=False)  # hero_title, phone, email, etc.
    content = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    updater = db.relationship("User", backref="content_updates")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'content_type': self.content_type,
            'section_key': self.section_key,
            'content': self.content,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }
