"""
User schemas for validation
"""
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password")
    
    @field_validator('username')
    @classmethod
    def validate_username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('نام کاربری نمی‌تواند خالی باشد')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('رمز عبور نمی‌تواند خالی باشد')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }
    )


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars, must include letter and number)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('نام کاربری نمی‌تواند خالی باشد')
        # Remove spaces
        v = v.strip()
        # Check if contains only alphanumeric and underscore
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('نام کاربری فقط می‌تواند شامل حروف، اعداد و underscore باشد')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError('رمز عبور باید حداقل 8 کاراکتر باشد')
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        if not (has_letter and has_number):
            raise ValueError('رمز عبور باید حداقل شامل یک حرف و یک عدد باشد')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "newuser",
                "email": "user@example.com",
                "password": "password123",
                "full_name": "John Doe"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    password: Optional[str] = Field(None, min_length=8, description="Password")
    is_active: Optional[bool] = Field(None, description="Active status")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('نام کاربری نمی‌تواند خالی باشد')
            v = v.strip()
            if not all(c.isalnum() or c == '_' for c in v):
                raise ValueError('نام کاربری فقط می‌تواند شامل حروف، اعداد و underscore باشد')
            return v.lower()
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('رمز عبور باید حداقل 8 کاراکتر باشد')
            has_letter = any(c.isalpha() for c in v)
            has_number = any(c.isdigit() for c in v)
            if not (has_letter and has_number):
                raise ValueError('رمز عبور باید حداقل شامل یک حرف و یک عدد باشد')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Updated",
                "is_active": True
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Active status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )

