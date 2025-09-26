from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app import db


class ProviderApplication(db.Model):
    __tablename__ = 'provider_application'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    representative_first_name = Column(String(100), nullable=False)
    representative_last_name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone_mobile = Column(String(20), nullable=False)
    phone_landline = Column(String(20), nullable=True)
    service_domain = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, nullable=False)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    
    # Relationship to the reviewer user
    reviewer = relationship("User", backref="reviewed_applications")
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'representative_first_name': self.representative_first_name,
            'representative_last_name': self.representative_last_name,
            'address': self.address,
            'phone_mobile': self.phone_mobile,
            'phone_landline': self.phone_landline,
            'service_domain': self.service_domain,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'is_approved': self.is_approved
        }

