"""
Comprehensive Tests for Service Layer Core Functionality
Tests: ApplicationService, CompanyService, UserService
"""
import pytest
from datetime import datetime, timezone
from backend.app import create_app, db
from backend.models.user import User
from backend.models.company import Company, Category
from backend.models.provider_application import ProviderApplication
from backend.services.user_service import UserService
from backend.services.company_service import CompanyService
from backend.services.application_service import ApplicationService
from backend.schemas.user import UserRegister, UserUpdate
from backend.schemas.company import CompanyCreate, CompanyUpdate
from backend.schemas.application import ApplicationReview
from backend.schemas.pagination import PaginationParams


@pytest.fixture(scope='function')
def app():
    """Create application for testing"""
    import tempfile
    import os
    
    # Set environment variable for test database BEFORE creating app
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['TESTING'] = 'True'
    
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Reinitialize db with test config
    with test_app.app_context():
        db.create_all()
        
        yield test_app
        
        # Cleanup
        db.session.remove()
        db.drop_all()
    
    # Clean up environment
    os.environ.pop('SQLALCHEMY_DATABASE_URI', None)
    os.environ.pop('TESTING', None)


@pytest.fixture
def app_context(app):
    """Create application context"""
    with app.app_context():
        # Clear any existing data
        db.session.rollback()
        yield
        # Cleanup after test
        db.session.rollback()


class TestUserService:
    """Tests for UserService"""
    
    def test_create_user_success(self, app_context):
        """Test successful user creation"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        user, error = UserService.create_user(user_data, role="user")
        
        assert error is None
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == "user"
        assert user.is_active is True
        assert user.check_password("SecurePass123!")
    
    def test_create_user_duplicate_username(self, app_context):
        """Test creating user with duplicate username"""
        user_data = UserRegister(
            username="testuser",
            email="test1@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        UserService.create_user(user_data, role="user")
        
        # Try to create another user with same username
        user_data2 = UserRegister(
            username="testuser",
            email="test2@example.com",
            password="SecurePass123!",
            full_name="Test User 2"
        )
        
        user, error = UserService.create_user(user_data2, role="user")
        
        assert user is None
        assert error == "نام کاربری قبلاً استفاده شده است"
    
    def test_create_user_duplicate_email(self, app_context):
        """Test creating user with duplicate email"""
        user_data = UserRegister(
            username="testuser1",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        UserService.create_user(user_data, role="user")
        
        # Try to create another user with same email
        user_data2 = UserRegister(
            username="testuser2",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User 2"
        )
        
        user, error = UserService.create_user(user_data2, role="user")
        
        assert user is None
        assert error == "ایمیل قبلاً استفاده شده است"
    
    def test_get_user_by_username(self, app_context):
        """Test getting user by username"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        created_user, _ = UserService.create_user(user_data, role="user")
        
        found_user = UserService.get_user_by_username("testuser")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "testuser"
    
    def test_get_user_by_email(self, app_context):
        """Test getting user by email"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        created_user, _ = UserService.create_user(user_data, role="user")
        
        found_user = UserService.get_user_by_email("test@example.com")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"
    
    def test_authenticate_success(self, app_context):
        """Test successful authentication"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        UserService.create_user(user_data, role="user")
        
        authenticated_user = UserService.authenticate("testuser", "SecurePass123!")
        
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
    
    def test_authenticate_wrong_password(self, app_context):
        """Test authentication with wrong password"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        UserService.create_user(user_data, role="user")
        
        authenticated_user = UserService.authenticate("testuser", "WrongPassword")
        
        assert authenticated_user is None
    
    def test_authenticate_inactive_user(self, app_context):
        """Test authentication with inactive user"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        user, _ = UserService.create_user(user_data, role="user")
        
        # Deactivate user
        user.is_active = False
        db.session.commit()
        
        authenticated_user = UserService.authenticate("testuser", "SecurePass123!")
        
        assert authenticated_user is None
    
    def test_update_user_success(self, app_context):
        """Test successful user update"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        user, _ = UserService.create_user(user_data, role="user")
        
        update_data = UserUpdate(
            full_name="Updated Name",
            email="updated@example.com"
        )
        
        updated_user, error = UserService.update_user(user.id, update_data)
        
        assert error is None
        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "updated@example.com"
    
    def test_update_user_duplicate_username(self, app_context):
        """Test updating user with duplicate username"""
        user1_data = UserRegister(
            username="user1",
            email="user1@example.com",
            password="SecurePass123!",
            full_name="User 1"
        )
        
        user2_data = UserRegister(
            username="user2",
            email="user2@example.com",
            password="SecurePass123!",
            full_name="User 2"
        )
        
        user1, _ = UserService.create_user(user1_data, role="user")
        user2, _ = UserService.create_user(user2_data, role="user")
        
        # Try to update user2 with user1's username
        update_data = UserUpdate(username="user1")
        
        updated_user, error = UserService.update_user(user2.id, update_data)
        
        assert updated_user is None
        assert error == "نام کاربری قبلاً استفاده شده است"
    
    def test_delete_user_success(self, app_context):
        """Test successful user deletion"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        user, _ = UserService.create_user(user_data, role="user")
        
        success, error = UserService.delete_user(user.id, current_user_id=999)
        
        assert success is True
        assert error is None
        assert UserService.get_user_by_id(user.id) is None
    
    def test_delete_user_self(self, app_context):
        """Test that user cannot delete themselves"""
        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        user, _ = UserService.create_user(user_data, role="user")
        
        success, error = UserService.delete_user(user.id, current_user_id=user.id)
        
        assert success is False
        assert error == "نمی‌توانید حساب کاربری خود را حذف کنید"
    
    def test_get_all_users_with_filters(self, app_context):
        """Test getting users with filters"""
        # Create users with different roles
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        UserService.create_user(admin_data, role="admin")
        
        user_data = UserRegister(
            username="user",
            email="user@example.com",
            password="SecurePass123!",
            full_name="Regular User"
        )
        UserService.create_user(user_data, role="user")
        
        # Filter by role
        users, total = UserService.get_all_users(role="admin")
        
        assert total == 1
        assert users[0].username == "admin"
    
    def test_get_all_users_with_pagination(self, app_context):
        """Test getting users with pagination"""
        # Create multiple users
        for i in range(5):
            user_data = UserRegister(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="SecurePass123!",
                full_name=f"User {i}"
            )
            UserService.create_user(user_data, role="user")
        
        # Get first page
        pagination = PaginationParams(page=1, per_page=2)
        users, total = UserService.get_all_users(pagination=pagination)
        
        assert total == 5
        assert len(users) == 2


class TestCompanyService:
    """Tests for CompanyService"""
    
    def test_create_company_success(self, app_context):
        """Test successful company creation"""
        # Create admin user first
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address",
            phone_landline="02112345678",
            latitude=35.6892,
            longitude=51.3890,
            is_active=True
        )
        
        company, error = CompanyService.create_company(company_data, created_by=admin.id)
        
        assert error is None
        assert company is not None
        assert company.name == "Test Company"
        assert company.phone_mobile == "09123456789"
        assert company.is_active is True
    
    def test_create_company_duplicate_phone(self, app_context):
        """Test creating company with duplicate phone"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        CompanyService.create_company(company_data, created_by=admin.id)
        
        # Try to create another company with same phone
        company_data2 = CompanyCreate(
            name="Test Company 2",
            phone="09123456789",
            address="Test Address 2"
        )
        
        company, error = CompanyService.create_company(company_data2, created_by=admin.id)
        
        assert company is None
        assert "شماره تلفن" in error
    
    def test_get_company_by_phone(self, app_context):
        """Test getting company by phone"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        created_company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        found_company = CompanyService.get_company_by_phone("09123456789")
        
        assert found_company is not None
        assert found_company.id == created_company.id
    
    def test_update_company_success(self, app_context):
        """Test successful company update"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        update_data = CompanyUpdate(
            name="Updated Company",
            address="Updated Address"
        )
        
        updated_company, error = CompanyService.update_company(company.id, update_data)
        
        assert error is None
        assert updated_company is not None
        assert updated_company.name == "Updated Company"
        assert updated_company.address == "Updated Address"
    
    def test_update_company_duplicate_phone(self, app_context):
        """Test updating company with duplicate phone"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company1_data = CompanyCreate(
            name="Company 1",
            phone="09123456789",
            address="Address 1"
        )
        
        company2_data = CompanyCreate(
            name="Company 2",
            phone="09123456788",
            address="Address 2"
        )
        
        company1, _ = CompanyService.create_company(company1_data, created_by=admin.id)
        company2, _ = CompanyService.create_company(company2_data, created_by=admin.id)
        
        # Try to update company2 with company1's phone
        update_data = CompanyUpdate(phone_mobile="09123456789")
        
        updated_company, error = CompanyService.update_company(company2.id, update_data)
        
        assert updated_company is None
        assert "شماره تلفن" in error
    
    def test_delete_company_success(self, app_context):
        """Test successful company deletion"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        success, error = CompanyService.delete_company(company.id)
        
        assert success is True
        assert error is None
        assert CompanyService.get_company_by_id(company.id) is None
    
    def test_toggle_company_status(self, app_context):
        """Test toggling company active status"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address",
            is_active=True
        )
        
        company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        # Toggle to inactive
        updated_company, error = CompanyService.toggle_company_status(company.id, False)
        
        assert error is None
        assert updated_company.is_active is False
        
        # Toggle back to active
        updated_company, error = CompanyService.toggle_company_status(company.id, True)
        
        assert error is None
        assert updated_company.is_active is True
    
    def test_add_category_to_company(self, app_context):
        """Test adding category to company"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        updated_company, error = CompanyService.add_category_to_company(company.id, "تعمیرات موتور")
        
        assert error is None
        assert updated_company is not None
        assert len(updated_company.categories) == 1
        assert updated_company.categories[0].name == "تعمیرات موتور"
    
    def test_add_duplicate_category_to_company(self, app_context):
        """Test adding duplicate category to company"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company_data = CompanyCreate(
            name="Test Company",
            phone="09123456789",
            address="Test Address"
        )
        
        company, _ = CompanyService.create_company(company_data, created_by=admin.id)
        
        # Add category first time
        CompanyService.add_category_to_company(company.id, "تعمیرات موتور")
        
        # Try to add same category again
        updated_company, error = CompanyService.add_category_to_company(company.id, "تعمیرات موتور")
        
        assert error is None
        assert len(updated_company.categories) == 1  # Should still be 1
    
    def test_get_all_companies_with_filters(self, app_context):
        """Test getting companies with filters"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        # Create active company
        active_company_data = CompanyCreate(
            name="Active Company",
            phone="09123456789",
            address="Address 1",
            is_active=True
        )
        CompanyService.create_company(active_company_data, created_by=admin.id)
        
        # Create inactive company
        inactive_company_data = CompanyCreate(
            name="Inactive Company",
            phone="09123456788",
            address="Address 2",
            is_active=False
        )
        CompanyService.create_company(inactive_company_data, created_by=admin.id)
        
        # Filter by active status
        companies, total = CompanyService.get_all_companies(is_active=True)
        
        assert total == 1
        assert companies[0].name == "Active Company"
    
    def test_get_companies_with_search(self, app_context):
        """Test searching companies"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        company1_data = CompanyCreate(
            name="Motor Repair Shop",
            phone="09123456789",
            address="Tehran"
        )
        CompanyService.create_company(company1_data, created_by=admin.id)
        
        company2_data = CompanyCreate(
            name="Body Shop",
            phone="09123456788",
            address="Shiraz"
        )
        CompanyService.create_company(company2_data, created_by=admin.id)
        
        # Search by name
        companies, total = CompanyService.get_all_companies(search="Motor")
        
        assert total == 1
        assert companies[0].name == "Motor Repair Shop"


class TestApplicationService:
    """Tests for ApplicationService"""
    
    def test_get_all_applications(self, app_context):
        """Test getting all applications"""
        # Create a test application
        application = ProviderApplication(
            company_name="Test Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            latitude=35.6892,
            longitude=51.3890,
            status="pending"
        )
        db.session.add(application)
        db.session.commit()
        
        applications, total = ApplicationService.get_all_applications()
        
        assert total == 1
        assert applications[0]['company_name'] == "Test Company"
    
    def test_get_applications_with_status_filter(self, app_context):
        """Test filtering applications by status"""
        # Create pending application
        pending_app = ProviderApplication(
            company_name="Pending Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(pending_app)
        
        # Create approved application
        approved_app = ProviderApplication(
            company_name="Approved Company",
            representative_first_name="Jane",
            representative_last_name="Smith",
            address="Test Address",
            phone_mobile="09123456788",
            service_domain="تعمیرات بدنه",
            status="approved",
            is_approved=True
        )
        db.session.add(approved_app)
        db.session.commit()
        
        # Filter by status
        applications, total = ApplicationService.get_all_applications(status="pending")
        
        assert total == 1
        assert applications[0]['status'] == "pending"
    
    def test_review_application_approve(self, app_context):
        """Test approving an application"""
        # Create admin user
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        # Create application
        application = ProviderApplication(
            company_name="Test Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(application)
        db.session.commit()
        
        # Review application
        review_data = ApplicationReview(
            is_approved=True,
            review_notes="Looks good"
        )
        
        reviewed_app, error = ApplicationService.review_application(
            application.id,
            review_data,
            admin.id
        )
        
        assert error is None
        assert reviewed_app is not None
        assert reviewed_app.is_approved is True
        assert reviewed_app.status == "approved"
        assert reviewed_app.reviewed_by == admin.id
    
    def test_review_application_reject(self, app_context):
        """Test rejecting an application"""
        # Create admin user
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        # Create application
        application = ProviderApplication(
            company_name="Test Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(application)
        db.session.commit()
        
        # Review application
        review_data = ApplicationReview(
            is_approved=False,
            review_notes="Incomplete information"
        )
        
        reviewed_app, error = ApplicationService.review_application(
            application.id,
            review_data,
            admin.id
        )
        
        assert error is None
        assert reviewed_app is not None
        assert reviewed_app.is_approved is False
        assert reviewed_app.status == "rejected"
        assert reviewed_app.review_notes == "Incomplete information"
    
    def test_review_nonexistent_application(self, app_context):
        """Test reviewing non-existent application"""
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        review_data = ApplicationReview(
            is_approved=True,
            review_notes="Test"
        )
        
        reviewed_app, error = ApplicationService.review_application(
            9999,  # Non-existent ID
            review_data,
            admin.id
        )
        
        assert reviewed_app is None
        assert error == "درخواست یافت نشد"
    
    def test_delete_application_success(self, app_context):
        """Test successful application deletion"""
        application = ProviderApplication(
            company_name="Test Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(application)
        db.session.commit()
        
        success, error = ApplicationService.delete_application(application.id)
        
        assert success is True
        assert error is None
        assert ApplicationService.get_application_by_id(application.id) is None
    
    def test_delete_nonexistent_application(self, app_context):
        """Test deleting non-existent application"""
        success, error = ApplicationService.delete_application(9999)
        
        assert success is False
        assert error == "درخواست یافت نشد"
    
    def test_get_dashboard_stats(self, app_context):
        """Test getting dashboard statistics"""
        # Create admin user
        admin_data = UserRegister(
            username="admin",
            email="admin@example.com",
            password="SecurePass123!",
            full_name="Admin User"
        )
        UserService.create_user(admin_data, role="admin")
        
        # Create applications with different statuses
        pending_app = ProviderApplication(
            company_name="Pending Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(pending_app)
        
        approved_app = ProviderApplication(
            company_name="Approved Company",
            representative_first_name="Jane",
            representative_last_name="Smith",
            address="Test Address",
            phone_mobile="09123456788",
            service_domain="تعمیرات بدنه",
            status="approved",
            is_approved=True
        )
        db.session.add(approved_app)
        
        rejected_app = ProviderApplication(
            company_name="Rejected Company",
            representative_first_name="Bob",
            representative_last_name="Johnson",
            address="Test Address",
            phone_mobile="09123456787",
            service_domain="تعمیرات برق",
            status="rejected",
            is_approved=False
        )
        db.session.add(rejected_app)
        db.session.commit()
        
        stats = ApplicationService.get_dashboard_stats()
        
        assert stats['total_applications'] == 3
        assert stats['pending_applications'] == 1
        assert stats['approved_applications'] == 1
        assert stats['rejected_applications'] == 1
    
    def test_get_applications_with_pagination(self, app_context):
        """Test getting applications with pagination"""
        # Create multiple applications
        for i in range(5):
            application = ProviderApplication(
                company_name=f"Company {i}",
                representative_first_name="John",
                representative_last_name="Doe",
                address="Test Address",
                phone_mobile=f"0912345678{i}",
                service_domain="تعمیرات موتور",
                status="pending"
            )
            db.session.add(application)
        db.session.commit()
        
        # Get first page
        pagination = PaginationParams(page=1, per_page=2)
        applications, total = ApplicationService.get_all_applications(pagination=pagination)
        
        assert total == 5
        assert len(applications) == 2
    
    def test_application_reviewer_info(self, app_context):
        """Test that reviewer information is included in application details"""
        # Create admin user
        admin_data = UserRegister(
            username="reviewer",
            email="reviewer@example.com",
            password="SecurePass123!",
            full_name="Reviewer Name"
        )
        admin, _ = UserService.create_user(admin_data, role="admin")
        
        # Create and review application
        application = ProviderApplication(
            company_name="Test Company",
            representative_first_name="John",
            representative_last_name="Doe",
            address="Test Address",
            phone_mobile="09123456789",
            service_domain="تعمیرات موتور",
            status="pending"
        )
        db.session.add(application)
        db.session.commit()
        
        review_data = ApplicationReview(
            is_approved=True,
            review_notes="Approved"
        )
        
        ApplicationService.review_application(application.id, review_data, admin.id)
        
        # Get applications
        applications, _ = ApplicationService.get_all_applications()
        
        assert applications[0]['reviewer_username'] == "reviewer"
        assert applications[0]['reviewer_name'] == "Reviewer Name"


def print_test_summary():
    """Print test execution summary"""
    print("\n" + "="*80)
    print("گزارش تست لایه سرویس (Service Layer)")
    print("="*80)
    print("\nحوزه‌های تست شده:")
    print("  1. UserService - مدیریت کاربران")
    print("     ✓ ایجاد کاربر")
    print("     ✓ احراز هویت")
    print("     ✓ بروزرسانی کاربر")
    print("     ✓ حذف کاربر")
    print("     ✓ اعتبارسنجی داده‌ها")
    print("\n  2. CompanyService - مدیریت شرکت‌ها")
    print("     ✓ ایجاد شرکت")
    print("     ✓ بروزرسانی شرکت")
    print("     ✓ حذف شرکت")
    print("     ✓ مدیریت دسته‌بندی‌ها")
    print("     ✓ جستجو و فیلتر")
    print("\n  3. ApplicationService - مدیریت درخواست‌ها")
    print("     ✓ دریافت درخواست‌ها")
    print("     ✓ بررسی و تایید/رد درخواست")
    print("     ✓ حذف درخواست")
    print("     ✓ آمار داشبورد")
    print("     ✓ صفحه‌بندی")
    print("\n" + "="*80)


if __name__ == '__main__':
    print_test_summary()
    pytest.main([__file__, '-v', '--tb=short'])

