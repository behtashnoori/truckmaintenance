"""
Provider application schemas for validation
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class ApplicationReview(BaseModel):
    """Schema for reviewing an application"""
    is_approved: bool = Field(..., description="Approval status")
    review_notes: Optional[str] = Field(default="", max_length=500, description="Review notes")
    
    @field_validator('review_notes')
    @classmethod
    def validate_review_notes(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return ""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_approved": True,
                "review_notes": "Application approved"
            }
        }
    )


class ApplicationResponse(BaseModel):
    """Schema for application response"""
    id: int = Field(..., description="Application ID")
    company_name: str = Field(..., description="Company name")
    representative_first_name: str = Field(..., description="Representative first name")
    representative_last_name: str = Field(..., description="Representative last name")
    address: str = Field(..., description="Company address")
    phone_mobile: str = Field(..., description="Mobile phone number")
    phone_landline: Optional[str] = Field(None, description="Landline phone number")
    service_domain: str = Field(..., description="Service domain")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    status: str = Field(..., description="Application status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    reviewed_by: Optional[int] = Field(None, description="Reviewer user ID")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    review_notes: Optional[str] = Field(None, description="Review notes")
    is_approved: Optional[bool] = Field(None, description="Approval status")
    reviewer_username: Optional[str] = Field(None, description="Reviewer username")
    reviewer_name: Optional[str] = Field(None, description="Reviewer full name")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "company_name": "شرکت نمونه",
                "representative_first_name": "علی",
                "representative_last_name": "احمدی",
                "address": "تهران، خیابان آزادی",
                "phone_mobile": "09123456789",
                "phone_landline": "02112345678",
                "service_domain": "تعمیرات موتور",
                "latitude": 35.6892,
                "longitude": 51.3890,
                "status": "pending",
                "created_at": "2024-01-01T00:00:00",
                "reviewed_by": None,
                "reviewed_at": None,
                "review_notes": None,
                "is_approved": None
            }
        }
    )


class ApplicationListResponse(BaseModel):
    """Schema for list of applications"""
    applications: List[ApplicationResponse] = Field(..., description="List of applications")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "applications": []
            }
        }
    )

