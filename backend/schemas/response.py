"""
Standard API response schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional


class ApiResponse(BaseModel):
    """Standard successful API response"""
    success: bool = Field(default=True, description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Example"}
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error API response"""
    success: bool = Field(default=False, description="Whether the request was successful")
    error: str = Field(..., description="Error message")
    details: Optional[Any] = Field(default=None, description="Additional error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Resource not found",
                "details": None
            }
        }
    )

