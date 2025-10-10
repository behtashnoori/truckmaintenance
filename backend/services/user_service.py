"""
User Service - Business logic for user operations
"""
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from ..app import db
from ..models.user import User
from ..schemas.user import UserRegister, UserUpdate
from ..schemas.pagination import PaginationParams
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for handling user business logic"""
    
    @staticmethod
    def get_all_users(
        pagination: Optional[PaginationParams] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """
        Get all users with optional filtering and pagination
        
        Args:
            pagination: Pagination parameters
            role: Filter by role
            is_active: Filter by active status
            
        Returns:
            Tuple of (users list, total count)
        """
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        
        users = query.all()
        return users, total
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get a user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User instance if authenticated, None otherwise
        """
        user = UserService.get_user_by_username(username)
        if user and user.check_password(password) and user.is_active:
            logger.info(f"User authenticated successfully: {username}")
            return user
        
        logger.warning(f"Failed authentication attempt for username: {username}")
        return None
    
    @staticmethod
    def create_user(user_data: UserRegister, role: str = "user") -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user
        
        Args:
            user_data: User registration data
            role: User role (default: "user")
            
        Returns:
            Tuple of (User instance or None, error message or None)
        """
        try:
            # Check if username already exists
            if UserService.get_user_by_username(user_data.username):
                return None, "نام کاربری قبلاً استفاده شده است"
            
            # Check if email already exists
            if UserService.get_user_by_email(user_data.email):
                return None, "ایمیل قبلاً استفاده شده است"
            
            # Create user
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=role,
                is_active=True
            )
            user.set_password(user_data.password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"User created successfully: ID={user.id}, Username={user.username}")
            return user, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating user: {str(e)}")
            return None, "خطا در ایجاد کاربر - نقض محدودیت یکتایی"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            return None, "خطا در ایجاد کاربر"
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> Tuple[Optional[User], Optional[str]]:
        """
        Update a user
        
        Args:
            user_id: User ID to update
            user_data: Update data
            
        Returns:
            Tuple of (User instance or None, error message or None)
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return None, "کاربر یافت نشد"
            
            # Update fields
            if user_data.username is not None:
                existing = UserService.get_user_by_username(user_data.username)
                if existing and existing.id != user_id:
                    return None, "نام کاربری قبلاً استفاده شده است"
                user.username = user_data.username
            
            if user_data.email is not None:
                existing = UserService.get_user_by_email(user_data.email)
                if existing and existing.id != user_id:
                    return None, "ایمیل قبلاً استفاده شده است"
                user.email = user_data.email
            
            if user_data.full_name is not None:
                user.full_name = user_data.full_name
            
            if user_data.is_active is not None:
                user.is_active = user_data.is_active
            
            if user_data.password:
                user.set_password(user_data.password)
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"User updated successfully: ID={user.id}")
            return user, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error updating user: {str(e)}")
            return None, "خطا در بروزرسانی کاربر - نقض محدودیت یکتایی"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {str(e)}", exc_info=True)
            return None, "خطا در بروزرسانی کاربر"
    
    @staticmethod
    def delete_user(user_id: int, current_user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a user
        
        Args:
            user_id: User ID to delete
            current_user_id: Current user ID (cannot delete self)
            
        Returns:
            Tuple of (success boolean, error message or None)
        """
        try:
            # Prevent deleting self
            if user_id == current_user_id:
                return False, "نمی‌توانید حساب کاربری خود را حذف کنید"
            
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False, "کاربر یافت نشد"
            
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"User deleted successfully: ID={user_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {str(e)}", exc_info=True)
            return False, "خطا در حذف کاربر"
    
    @staticmethod
    def get_user_statistics() -> dict:
        """
        Get user statistics
        
        Returns:
            Dictionary with user statistics
        """
        try:
            stats = {
                "total_users": User.query.count(),
                "active_users": User.query.filter_by(is_active=True).count(),
                "admin_users": User.query.filter_by(role='admin').count(),
                "support_users": User.query.filter_by(role='support').count(),
                "business_expert_users": User.query.filter_by(role='business_expert').count()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}", exc_info=True)
            return {}

