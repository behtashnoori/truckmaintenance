"""
Pydantic schemas for request/response validation
"""
from .company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CategorySchema
)
from .user import (
    UserLogin,
    UserRegister,
    UserUpdate,
    UserResponse
)
from .application import (
    ApplicationReview,
    ApplicationResponse,
    ApplicationListResponse
)
from .pagination import PaginationParams, PaginatedResponse
from .response import ApiResponse, ErrorResponse

__all__ = [
    # Company schemas
    'CompanyCreate',
    'CompanyUpdate',
    'CompanyResponse',
    'CompanyListResponse',
    'CategorySchema',
    # User schemas
    'UserLogin',
    'UserRegister',
    'UserUpdate',
    'UserResponse',
    # Application schemas
    'ApplicationReview',
    'ApplicationResponse',
    'ApplicationListResponse',
    # Pagination
    'PaginationParams',
    'PaginatedResponse',
    # Response
    'ApiResponse',
    'ErrorResponse'
]

