"""
Company and Category schemas for validation
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class CategorySchema(BaseModel):
    """Category schema"""
    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    
    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    """Schema for creating a new company"""
    name: str = Field(..., min_length=2, max_length=255, description="Company name")
    phone: str = Field(..., alias="phone", description="Mobile phone number")
    address: Optional[str] = Field(default="", description="Company address")
    phone_landline: Optional[str] = Field(default=None, description="Landline phone number")
    latitude: Optional[float] = Field(default=0.0, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(default=0.0, ge=-180, le=180, description="Longitude")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Iranian mobile phone validation
        pattern = r'^09\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('شماره موبایل باید با فرمت 09xxxxxxxxx باشد')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('نام شرکت نمی‌تواند خالی باشد')
        return v.strip()
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "شرکت نمونه",
                "phone": "09123456789",
                "address": "تهران، خیابان آزادی",
                "latitude": 35.6892,
                "longitude": 51.3890,
                "is_active": True
            }
        }
    )


class CompanyUpdate(BaseModel):
    """Schema for updating a company"""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Company name")
    address: Optional[str] = Field(None, description="Company address")
    phone_mobile: Optional[str] = Field(None, description="Mobile phone number")
    phone_landline: Optional[str] = Field(None, description="Landline phone number")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    is_active: Optional[bool] = Field(None, description="Active status")
    
    @field_validator('phone_mobile')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            pattern = r'^09\d{9}$'
            if not re.match(pattern, v):
                raise ValueError('شماره موبایل باید با فرمت 09xxxxxxxxx باشد')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "شرکت بروزرسانی شده",
                "address": "تهران، خیابان ولیعصر",
                "is_active": True
            }
        }
    )


class CompanyResponse(BaseModel):
    """Schema for company response"""
    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    address: str = Field(..., description="Company address")
    phone_mobile: str = Field(..., description="Mobile phone number")
    phone_landline: Optional[str] = Field(None, description="Landline phone number")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    is_active: bool = Field(..., description="Active status")
    categories: List[CategorySchema] = Field(default=[], description="Company categories")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[int] = Field(None, description="Creator user ID")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "شرکت نمونه",
                "address": "تهران، خیابان آزادی",
                "phone_mobile": "09123456789",
                "phone_landline": "02112345678",
                "latitude": 35.6892,
                "longitude": 51.3890,
                "is_active": True,
                "categories": [{"id": 1, "name": "تعمیرات موتور"}],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "created_by": 1
            }
        }
    )


class CompanyListResponse(BaseModel):
    """Schema for list of companies"""
    providers: List[CompanyResponse] = Field(..., description="List of companies")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "providers": [
                    {
                        "id": 1,
                        "name": "شرکت نمونه",
                        "address": "تهران",
                        "phone_mobile": "09123456789",
                        "is_active": True,
                        "categories": []
                    }
                ]
            }
        }
    )

