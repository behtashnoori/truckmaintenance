from ..app import db
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)


class VehicleType(db.Model):
    __tablename__ = "vehicle_type"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # نام فارسی
    name_en = db.Column(db.String(100), nullable=False, unique=True)  # نام انگلیسی (truck, semi, bus)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)  # نام آیکون
    capacity_min = db.Column(db.Integer, nullable=True)  # حداقل ظرفیت (تن)
    capacity_max = db.Column(db.Integer, nullable=True)  # حداکثر ظرفیت (تن)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    def to_dict(self):
        """Convert vehicle type to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'description': self.description,
            'icon': self.icon,
            'capacity_min': self.capacity_min,
            'capacity_max': self.capacity_max,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

