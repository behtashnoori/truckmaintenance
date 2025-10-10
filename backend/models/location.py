from ..app import db
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)


class Location(db.Model):
    __tablename__ = "location"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'province', 'county', or 'city'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Self-referential relationship for hierarchical structure
    children = db.relationship('Location', 
                               backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')
    
    def to_dict(self, include_children=False):
        """Convert location to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'lat': self.latitude,
            'lon': self.longitude,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_children:
            result['children'] = [child.to_dict(include_children=False) for child in self.children.all()]
        
        return result

