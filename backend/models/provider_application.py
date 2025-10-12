from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..app import db
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time - used for database defaults"""
    return datetime.now(timezone.utc)


# Association table for ProviderApplication and Category (many-to-many)
provider_application_category = Table('provider_application_category', db.Model.metadata,
    Column('application_id', Integer, ForeignKey('provider_application.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id', ondelete='CASCADE'), primary_key=True)
)


class ProviderApplication(db.Model):
    __tablename__ = 'provider_application'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False, index=True)
    representative_first_name = Column(String(100), nullable=False)
    representative_last_name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone_mobile = Column(String(20), nullable=False, unique=True, index=True)
    phone_landline = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, nullable=False, default=utc_now, index=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    
    # Duplicate prevention and tracking fields
    reapplication_count = Column(Integer, default=1, nullable=False)
    last_submitted_at = Column(DateTime, nullable=False, default=utc_now)
    fuzzy_match_warning = Column(Boolean, default=False)
    similar_company_names = Column(Text, nullable=True)
    
    # Relationship to the reviewer user
    reviewer = relationship("User", backref="reviewed_applications")
    
    # Many-to-many relationship with Category
    categories = relationship('Category', secondary=provider_application_category, backref='applications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'representative_first_name': self.representative_first_name,
            'representative_last_name': self.representative_last_name,
            'address': self.address,
            'phone_mobile': self.phone_mobile,
            'phone_landline': self.phone_landline,
            'service_categories': [cat.name for cat in self.categories],
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'is_approved': self.is_approved,
            'reapplication_count': self.reapplication_count,
            'fuzzy_match_warning': self.fuzzy_match_warning,
            'similar_company_names': self.similar_company_names
        }

