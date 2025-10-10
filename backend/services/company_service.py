"""
Company Service - Business logic for company operations
"""
from typing import List, Optional, Tuple
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy import or_, func
from ..app import db
from ..models.company import Company, Category
from ..schemas.company import CompanyCreate, CompanyUpdate
from ..schemas.pagination import PaginationParams
import logging
import math

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for handling company business logic"""
    
    @staticmethod
    def get_all_companies(
        pagination: Optional[PaginationParams] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Company], int]:
        """
        Get all companies with optional filtering and pagination
        
        Args:
            pagination: Pagination parameters
            is_active: Filter by active status
            status: Filter by status (alias for is_active)
            category_id: Filter by category
            search: Search in name, address, phone
            
        Returns:
            Tuple of (companies list, total count)
        """
        query = Company.query
        
        # Apply filters
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        elif status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        if category_id:
            query = query.join(Company.categories).filter(Category.id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.address.ilike(search_term),
                    Company.phone_mobile.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        
        companies = query.all()
        return companies, total
    
    @staticmethod
    def get_company_by_id(company_id: int) -> Optional[Company]:
        """Get a company by ID"""
        return Company.query.get(company_id)
    
    @staticmethod
    def get_company_by_phone(phone: str) -> Optional[Company]:
        """Get a company by phone number"""
        return Company.query.filter_by(phone_mobile=phone).first()
    
    @staticmethod
    def create_company(company_data: CompanyCreate, created_by: int) -> Tuple[Optional[Company], Optional[str]]:
        """
        Create a new company
        
        Args:
            company_data: Company creation data
            created_by: User ID creating the company
            
        Returns:
            Tuple of (Company instance or None, error message or None)
        """
        try:
            # Check if company already exists
            existing_company = CompanyService.get_company_by_phone(company_data.phone)
            if existing_company:
                logger.warning(f"Duplicate company phone attempted: {company_data.phone[:3]}***")
                return None, "شرکت با این شماره تلفن قبلاً ثبت شده است"
            
            # Create company
            company = Company(
                name=company_data.name,
                phone_mobile=company_data.phone,
                address=company_data.address or "",
                phone_landline=company_data.phone_landline,
                latitude=company_data.latitude or 0.0,
                longitude=company_data.longitude or 0.0,
                is_active=company_data.is_active if company_data.is_active is not None else True,
                created_by=created_by
            )
            
            db.session.add(company)
            db.session.commit()
            
            logger.info(f"Company created successfully: ID={company.id}, Name={company.name}")
            return company, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating company: {str(e)}")
            
            if "uq_company_phone_mobile" in str(e):
                return None, "شرکت با این شماره تلفن قبلاً ثبت شده است"
            
            return None, "خطا در ایجاد شرکت - نقض محدودیت یکتایی"
            
        except DatabaseError as e:
            db.session.rollback()
            logger.error(f"Database error creating company: {str(e)}")
            return None, "خطای دیتابیس در ایجاد شرکت"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error creating company: {str(e)}", exc_info=True)
            return None, "خطای سرور در ایجاد شرکت"
    
    @staticmethod
    def update_company(company_id: int, company_data: CompanyUpdate) -> Tuple[Optional[Company], Optional[str]]:
        """
        Update a company
        
        Args:
            company_id: Company ID to update
            company_data: Update data
            
        Returns:
            Tuple of (Company instance or None, error message or None)
        """
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return None, "شرکت یافت نشد"
            
            # Update fields
            if company_data.name is not None:
                company.name = company_data.name
            if company_data.address is not None:
                company.address = company_data.address
            if company_data.phone_mobile is not None:
                # Check if phone is already used by another company
                existing = CompanyService.get_company_by_phone(company_data.phone_mobile)
                if existing and existing.id != company_id:
                    return None, "شماره تلفن قبلاً توسط شرکت دیگری استفاده شده است"
                company.phone_mobile = company_data.phone_mobile
            if company_data.phone_landline is not None:
                company.phone_landline = company_data.phone_landline
            if company_data.latitude is not None:
                company.latitude = company_data.latitude
            if company_data.longitude is not None:
                company.longitude = company_data.longitude
            if company_data.is_active is not None:
                company.is_active = company_data.is_active
            
            db.session.commit()
            logger.info(f"Company updated successfully: ID={company.id}")
            return company, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error updating company: {str(e)}")
            return None, "خطا در بروزرسانی شرکت - نقض محدودیت یکتایی"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating company: {str(e)}", exc_info=True)
            return None, "خطا در بروزرسانی شرکت"
    
    @staticmethod
    def delete_company(company_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a company
        
        Args:
            company_id: Company ID to delete
            
        Returns:
            Tuple of (success boolean, error message or None)
        """
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return False, "شرکت یافت نشد"
            
            db.session.delete(company)
            db.session.commit()
            
            logger.info(f"Company deleted successfully: ID={company_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting company: {str(e)}", exc_info=True)
            return False, "خطا در حذف شرکت"
    
    @staticmethod
    def toggle_company_status(company_id: int, is_active: bool) -> Tuple[Optional[Company], Optional[str]]:
        """
        Toggle company active status
        
        Args:
            company_id: Company ID
            is_active: New active status
            
        Returns:
            Tuple of (Company instance or None, error message or None)
        """
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return None, "شرکت یافت نشد"
            
            company.is_active = is_active
            db.session.commit()
            
            logger.info(f"Company status toggled: ID={company_id}, Active={is_active}")
            return company, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling company status: {str(e)}", exc_info=True)
            return None, "خطا در تغییر وضعیت شرکت"
    
    @staticmethod
    def add_category_to_company(company_id: int, category_name: str) -> Tuple[Optional[Company], Optional[str]]:
        """
        Add a category to a company
        
        Args:
            company_id: Company ID
            category_name: Category name
            
        Returns:
            Tuple of (Company instance or None, error message or None)
        """
        try:
            company = CompanyService.get_company_by_id(company_id)
            if not company:
                return None, "شرکت یافت نشد"
            
            # Get or create category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.flush()
            
            # Add category if not already added
            if category not in company.categories:
                company.categories.append(category)
                db.session.commit()
                logger.info(f"Category added to company: CompanyID={company_id}, Category={category_name}")
            
            return company, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding category to company: {str(e)}", exc_info=True)
            return None, "خطا در افزودن دسته‌بندی"
    
    @staticmethod
    def get_nearby_companies(latitude: float, longitude: float, radius_km: float = 10.0) -> List[Company]:
        """
        Get companies within a radius (simplified - not using PostGIS)
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby companies
        """
        # Simple bounding box calculation (not accurate for large distances)
        # For production, use PostGIS or similar
        lat_delta = radius_km / 111.0  # Approximately 111 km per degree latitude
        lon_delta = radius_km / (111.0 * abs(func.cos(func.radians(latitude))))
        
        companies = Company.query.filter(
            Company.is_active == True,
            Company.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Company.longitude.between(longitude - lon_delta, longitude + lon_delta)
        ).all()
        
        return companies
    
    @staticmethod
    def get_company_statistics() -> dict:
        """
        Get company statistics
        
        Returns:
            Dictionary with company statistics
        """
        try:
            stats = {
                "total_companies": Company.query.count(),
                "active_companies": Company.query.filter_by(is_active=True).count(),
                "total_providers": Company.query.count()  # Assuming each company is a provider
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting company statistics: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def get_system_settings() -> dict:
        """
        Get system settings
        
        Returns:
            Dictionary with system settings
        """
        try:
            # For now, return default settings
            # In a real application, these would be stored in a settings table
            settings_data = {
                "site_name": "سامانه مدیریت ارائه‌دهندگان خدمات",
                "site_description": "سامانه جامع مدیریت و رزرو خدمات ارائه‌دهندگان خودروهای سنگین",
                "contact_email": "info@truckmaintenance.local",
                "admin_email": "admin@truckmaintenance.local",
                "max_file_size": 10,
                "allowed_file_types": ["jpg", "png", "pdf", "doc", "docx"],
                "email_notifications": True,
                "sms_notifications": False,
                "maintenance_mode": False,
                "auto_approval": False,
                "max_applications_per_day": 100,
                "session_timeout": 60,
                "password_policy": {
                    "min_length": 8,
                    "require_special_chars": True,
                    "require_numbers": True,
                    "require_uppercase": True,
                },
                "backup_settings": {
                    "auto_backup": True,
                    "backup_frequency": "daily",
                    "retention_days": 30,
                }
            }
            return settings_data
        except Exception as e:
            logger.error(f"Error getting system settings: {str(e)}", exc_info=True)
            return {}

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r

