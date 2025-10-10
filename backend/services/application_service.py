"""
Application Service - Business logic for provider application operations
"""
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from ..app import db
from ..models.provider_application import ProviderApplication
from ..models.user import User
from ..schemas.application import ApplicationReview
from ..schemas.pagination import PaginationParams
import logging

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service for handling provider application business logic"""
    
    @staticmethod
    def get_all_applications(
        pagination: Optional[PaginationParams] = None,
        status: Optional[str] = None,
        is_approved: Optional[bool] = None
    ) -> Tuple[List[dict], int]:
        """
        Get all applications with optional filtering and pagination
        
        Args:
            pagination: Pagination parameters
            status: Filter by status
            is_approved: Filter by approval status
            
        Returns:
            Tuple of (applications list with reviewer info, total count)
        """
        query = ProviderApplication.query
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        
        if is_approved is not None:
            query = query.filter_by(is_approved=is_approved)
        
        # Get total count
        total = query.count()
        
        # Order by creation date (newest first) - MUST be before pagination
        query = query.order_by(ProviderApplication.created_at.desc())
        
        # Apply pagination AFTER ordering
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        
        applications = query.all()
        
        # Build response with reviewer information
        applications_list = []
        for app in applications:
            app_data = {
                "id": app.id,
                "company_name": app.company_name,
                "representative_first_name": app.representative_first_name,
                "representative_last_name": app.representative_last_name,
                "address": app.address,
                "phone_mobile": app.phone_mobile,
                "phone_landline": app.phone_landline,
                "service_domain": app.service_domain,
                "latitude": app.latitude,
                "longitude": app.longitude,
                "status": app.status,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "reviewed_by": app.reviewed_by,
                "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
                "review_notes": app.review_notes,
                "is_approved": app.is_approved,
                "reviewer_username": None,
                "reviewer_name": None
            }
            
            # Get reviewer information if available
            if app.reviewed_by:
                reviewer = User.query.get(app.reviewed_by)
                if reviewer:
                    app_data["reviewer_username"] = reviewer.username
                    app_data["reviewer_name"] = reviewer.full_name
            
            applications_list.append(app_data)
        
        return applications_list, total
    
    @staticmethod
    def get_application_by_id(app_id: int) -> Optional[ProviderApplication]:
        """Get an application by ID"""
        return ProviderApplication.query.get(app_id)
    
    @staticmethod
    def review_application(
        app_id: int,
        review_data: ApplicationReview,
        reviewer_id: int
    ) -> Tuple[Optional[ProviderApplication], Optional[str]]:
        """
        Review a provider application
        
        Args:
            app_id: Application ID
            review_data: Review data
            reviewer_id: ID of user reviewing the application
            
        Returns:
            Tuple of (Application instance or None, error message or None)
        """
        try:
            application = ApplicationService.get_application_by_id(app_id)
            if not application:
                return None, "درخواست یافت نشد"
            
            # Update application
            application.reviewed_by = reviewer_id
            application.reviewed_at = datetime.now(timezone.utc)
            application.review_notes = review_data.review_notes or ""
            application.is_approved = review_data.is_approved
            application.status = 'approved' if review_data.is_approved else 'rejected'
            
            db.session.commit()
            
            logger.info(f"Application reviewed: ID={app_id}, Approved={review_data.is_approved}")
            return application, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reviewing application: {str(e)}", exc_info=True)
            return None, "خطا در بررسی درخواست"
    
    @staticmethod
    def delete_application(app_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete an application
        
        Args:
            app_id: Application ID to delete
            
        Returns:
            Tuple of (success boolean, error message or None)
        """
        try:
            application = ApplicationService.get_application_by_id(app_id)
            if not application:
                return False, "درخواست یافت نشد"
            
            db.session.delete(application)
            db.session.commit()
            
            logger.info(f"Application deleted successfully: ID={app_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting application: {str(e)}", exc_info=True)
            return False, "خطا در حذف درخواست"
    
    @staticmethod
    def get_dashboard_stats() -> dict:
        """
        Get dashboard statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = {
                "total_applications": ProviderApplication.query.count(),
                "pending_applications": ProviderApplication.query.filter_by(status='pending').count(),
                "approved_applications": ProviderApplication.query.filter_by(is_approved=True).count(),
                "rejected_applications": ProviderApplication.query.filter_by(is_approved=False, status='rejected').count(),
                "active_support": User.query.filter_by(role='support', is_active=True).count()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def get_category_statistics(period: str = 'month') -> List[dict]:
        """
        Get category statistics
        
        Args:
            period: Time period for statistics
            
        Returns:
            List of category statistics
        """
        try:
            # For now, return empty list
            # In a real application, this would query the database for actual category stats
            return []
        except Exception as e:
            logger.error(f"Error getting category statistics: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    def get_monthly_statistics(period: str = 'month') -> List[dict]:
        """
        Get monthly statistics
        
        Args:
            period: Time period for statistics
            
        Returns:
            List of monthly statistics
        """
        try:
            # For now, return empty list
            # In a real application, this would query the database for actual monthly stats
            return []
        except Exception as e:
            logger.error(f"Error getting monthly statistics: {str(e)}", exc_info=True)
            return []

