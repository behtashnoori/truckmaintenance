from ..app import db
from sqlalchemy import UniqueConstraint, Table, Column, Integer, ForeignKey
from datetime import datetime, timezone

def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)

# Association Table for Company and Category
company_category_association = Table('company_category', db.Model.metadata,
    Column('company_id', Integer, ForeignKey('company.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id'), primary_key=True)
)

class Company(db.Model):
    __tablename__ = "company"
    __table_args__ = (
        UniqueConstraint("phone_mobile", name="uq_company_phone_mobile"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)  # Alias for name
    address = db.Column(db.Text, nullable=False)
    phone_mobile = db.Column(db.String(20), nullable=False)
    phone_landline = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    service_radius_km = db.Column(db.Float, default=50.0, nullable=False)
    is_24_7 = db.Column(db.Boolean, default=False, nullable=False)
    vehicle_types = db.Column(db.JSON, nullable=True)  # ['truck', 'semi', 'bus']
    description = db.Column(db.Text, nullable=True)
    services = db.Column(db.Text, nullable=True)
    working_hours = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Audit trail fields
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Many-to-Many relationship with Category
    categories = db.relationship('Category', secondary=company_category_association, back_populates='companies')
    
    # Relationship with creator user (temporarily disabled to fix import issues)
    # creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies', lazy='select')
    
    def __init__(self, **kwargs):
        """Initialize Company and sync name/company_name fields"""
        # Sync name and company_name
        if 'name' in kwargs and 'company_name' not in kwargs:
            kwargs['company_name'] = kwargs['name']
        elif 'company_name' in kwargs and 'name' not in kwargs:
            kwargs['name'] = kwargs['company_name']
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Convert company to dictionary"""
        return {
            'id': self.id,
            'name': self.name or self.company_name,
            'company_name': self.company_name or self.name,
            'address': self.address,
            'phone_mobile': self.phone_mobile,
            'phone_landline': self.phone_landline,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'service_radius_km': self.service_radius_km,
            'is_24_7': self.is_24_7,
            'vehicle_types': self.vehicle_types or [],
            'description': self.description,
            'services': self.services,
            'working_hours': self.working_hours,
            'is_active': self.is_active,
            'categories': [cat.name for cat in self.categories],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationship back to Company
    companies = db.relationship('Company', secondary=company_category_association, back_populates='categories')
