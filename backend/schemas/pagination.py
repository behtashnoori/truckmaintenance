"""
Pagination schemas and utilities
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Any, Optional, Generic, TypeVar


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, description="Page number (starting from 1)")
    per_page: int = Field(default=20, description="Items per page (max 100)")
    
    @field_validator('page')
    @classmethod
    def validate_page(cls, v):
        if v < 1:
            return 1
        return v
    
    @field_validator('per_page')
    @classmethod
    def validate_per_page(cls, v):
        if v < 1:
            return 1
        if v > 100:
            return 100
        return v
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.per_page


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    success: bool = Field(default=True)
    data: List[T] = Field(..., description="List of items")
    pagination: dict = Field(..., description="Pagination metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }
    )
    
    @staticmethod
    def create(items: List[Any], page: int, per_page: int, total: int) -> dict:
        """Create paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

