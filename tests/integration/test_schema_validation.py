"""
Comprehensive Schema Validation Tests
Tests all Pydantic schemas for proper validation and error handling
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from backend.schemas import (
    # User schemas
    UserLogin,
    UserRegister,
    UserUpdate,
    UserResponse,
    # Company schemas
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CategorySchema,
    # Application schemas
    ApplicationReview,
    ApplicationResponse,
    ApplicationListResponse,
    # Pagination
    PaginationParams,
    PaginatedResponse,
    # Response
    ApiResponse,
    ErrorResponse
)


# ==================== User Schema Tests ====================

class TestUserLoginSchema:
    """Test UserLogin schema validation"""
    
    def test_valid_user_login(self):
        """Test valid user login data"""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        user_login = UserLogin(**data)
        assert user_login.username == "testuser"
        assert user_login.password == "password123"
    
    def test_username_too_short(self):
        """Test username validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="ab", password="password123")
        assert "username" in str(exc_info.value)
    
    def test_username_too_long(self):
        """Test username validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="a" * 51, password="password123")
        assert "username" in str(exc_info.value)
    
    def test_password_too_short(self):
        """Test password validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="testuser", password="12345")
        assert "password" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        with pytest.raises(ValidationError):
            UserLogin(username="testuser")
        
        with pytest.raises(ValidationError):
            UserLogin(password="password123")


class TestUserRegisterSchema:
    """Test UserRegister schema validation"""
    
    def test_valid_user_register(self):
        """Test valid user registration"""
        data = {
            "username": "newuser",
            "email": "user@example.com",
            "password": "password123",
            "full_name": "John Doe"
        }
        user_register = UserRegister(**data)
        assert user_register.username == "newuser"
        assert user_register.email == "user@example.com"
        assert user_register.password == "password123"
        assert user_register.full_name == "John Doe"
    
    def test_username_lowercase_conversion(self):
        """Test username is converted to lowercase"""
        data = {
            "username": "TestUser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_register = UserRegister(**data)
        assert user_register.username == "testuser"
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_username_validation_alphanumeric(self):
        """Test username validation - should accept alphanumeric and underscore"""
        valid_usernames = ["user123", "test_user", "user_123"]
        for username in valid_usernames:
            data = {
                "username": username,
                "email": "user@example.com",
                "password": "password123"
            }
            user_register = UserRegister(**data)
            assert user_register.username == username.lower()
    
    def test_optional_full_name(self):
        """Test full_name is optional"""
        data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_register = UserRegister(**data)
        assert user_register.full_name is None
    
    def test_full_name_max_length(self):
        """Test full_name max length validation"""
        with pytest.raises(ValidationError):
            UserRegister(
                username="testuser",
                email="user@example.com",
                password="password123",
                full_name="a" * 101
            )


class TestUserUpdateSchema:
    """Test UserUpdate schema validation"""
    
    def test_all_fields_optional(self):
        """Test all fields are optional"""
        user_update = UserUpdate()
        assert user_update.username is None
        assert user_update.email is None
        assert user_update.full_name is None
        assert user_update.password is None
        assert user_update.is_active is None
    
    def test_partial_update(self):
        """Test partial update with some fields"""
        data = {
            "full_name": "Updated Name",
            "is_active": False
        }
        user_update = UserUpdate(**data)
        assert user_update.full_name == "Updated Name"
        assert user_update.is_active == False
        assert user_update.username is None
        assert user_update.email is None
    
    def test_password_min_length_when_provided(self):
        """Test password validation when provided"""
        with pytest.raises(ValidationError):
            UserUpdate(password="12345")


class TestUserResponseSchema:
    """Test UserResponse schema validation"""
    
    def test_valid_user_response(self):
        """Test valid user response"""
        data = {
            "id": 1,
            "username": "testuser",
            "email": "user@example.com",
            "full_name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        user_response = UserResponse(**data)
        assert user_response.id == 1
        assert user_response.username == "testuser"
        assert user_response.role == "user"
        assert user_response.is_active == True
    
    def test_required_fields(self):
        """Test required fields"""
        with pytest.raises(ValidationError):
            UserResponse(id=1, username="test", email="test@test.com")


# ==================== Company Schema Tests ====================

class TestCompanyCreateSchema:
    """Test CompanyCreate schema validation"""
    
    def test_valid_company_create(self):
        """Test valid company creation"""
        data = {
            "name": "شرکت تست",
            "phone": "09123456789",
            "address": "تهران",
            "latitude": 35.6892,
            "longitude": 51.3890
        }
        company = CompanyCreate(**data)
        assert company.name == "شرکت تست"
        assert company.phone == "09123456789"
        assert company.address == "تهران"
    
    def test_phone_validation_valid(self):
        """Test valid Iranian mobile phone numbers"""
        valid_phones = [
            "09123456789",
            "09351234567",
            "09901234567"
        ]
        for phone in valid_phones:
            data = {
                "name": "تست",
                "phone": phone,
                "address": "تهران"
            }
            company = CompanyCreate(**data)
            assert company.phone == phone
    
    def test_phone_validation_invalid(self):
        """Test invalid phone numbers"""
        invalid_phones = [
            "9123456789",      # Missing 0
            "091234567",       # Too short
            "09123456789012",  # Too long
            "08123456789",     # Doesn't start with 09
            "abc123456789",    # Contains letters
            "09-12-345-6789",  # Contains dashes
        ]
        for phone in invalid_phones:
            with pytest.raises(ValidationError) as exc_info:
                CompanyCreate(name="تست", phone=phone, address="تهران")
            assert "phone" in str(exc_info.value).lower() or "شماره" in str(exc_info.value)
    
    def test_name_validation_empty(self):
        """Test empty name validation"""
        with pytest.raises(ValidationError):
            CompanyCreate(name="", phone="09123456789", address="تهران")
        
        with pytest.raises(ValidationError):
            CompanyCreate(name="   ", phone="09123456789", address="تهران")
    
    def test_name_trim_whitespace(self):
        """Test name whitespace trimming"""
        data = {
            "name": "  شرکت تست  ",
            "phone": "09123456789",
            "address": "تهران"
        }
        company = CompanyCreate(**data)
        assert company.name == "شرکت تست"
    
    def test_latitude_validation(self):
        """Test latitude range validation"""
        # Valid latitudes
        for lat in [-90, -45, 0, 45, 90]:
            company = CompanyCreate(
                name="تست",
                phone="09123456789",
                latitude=lat,
                longitude=0
            )
            assert company.latitude == lat
        
        # Invalid latitudes
        with pytest.raises(ValidationError):
            CompanyCreate(name="تست", phone="09123456789", latitude=91, longitude=0)
        
        with pytest.raises(ValidationError):
            CompanyCreate(name="تست", phone="09123456789", latitude=-91, longitude=0)
    
    def test_longitude_validation(self):
        """Test longitude range validation"""
        # Valid longitudes
        for lng in [-180, -90, 0, 90, 180]:
            company = CompanyCreate(
                name="تست",
                phone="09123456789",
                latitude=0,
                longitude=lng
            )
            assert company.longitude == lng
        
        # Invalid longitudes
        with pytest.raises(ValidationError):
            CompanyCreate(name="تست", phone="09123456789", latitude=0, longitude=181)
        
        with pytest.raises(ValidationError):
            CompanyCreate(name="تست", phone="09123456789", latitude=0, longitude=-181)
    
    def test_default_values(self):
        """Test default values"""
        company = CompanyCreate(name="تست", phone="09123456789")
        assert company.address == ""
        assert company.latitude == 0.0
        assert company.longitude == 0.0
        assert company.is_active == True
        assert company.phone_landline is None
    
    def test_name_length_validation(self):
        """Test name length constraints"""
        # Too short
        with pytest.raises(ValidationError):
            CompanyCreate(name="ت", phone="09123456789")
        
        # Too long
        with pytest.raises(ValidationError):
            CompanyCreate(name="ت" * 256, phone="09123456789")


class TestCompanyUpdateSchema:
    """Test CompanyUpdate schema validation"""
    
    def test_all_fields_optional(self):
        """Test all fields are optional"""
        company_update = CompanyUpdate()
        assert company_update.name is None
        assert company_update.address is None
        assert company_update.phone_mobile is None
    
    def test_partial_update(self):
        """Test partial update"""
        data = {
            "name": "شرکت بروز شده",
            "is_active": False
        }
        company_update = CompanyUpdate(**data)
        assert company_update.name == "شرکت بروز شده"
        assert company_update.is_active == False
        assert company_update.address is None
    
    def test_phone_validation_when_provided(self):
        """Test phone validation when provided"""
        # Valid
        company_update = CompanyUpdate(phone_mobile="09123456789")
        assert company_update.phone_mobile == "09123456789"
        
        # Invalid
        with pytest.raises(ValidationError):
            CompanyUpdate(phone_mobile="123456789")
    
    def test_coordinates_validation(self):
        """Test coordinate validation when provided"""
        # Valid
        company_update = CompanyUpdate(latitude=35.6892, longitude=51.3890)
        assert company_update.latitude == 35.6892
        
        # Invalid
        with pytest.raises(ValidationError):
            CompanyUpdate(latitude=95)


class TestCompanyResponseSchema:
    """Test CompanyResponse schema validation"""
    
    def test_valid_company_response(self):
        """Test valid company response"""
        data = {
            "id": 1,
            "name": "شرکت تست",
            "address": "تهران",
            "phone_mobile": "09123456789",
            "latitude": 35.6892,
            "longitude": 51.3890,
            "is_active": True,
            "categories": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": 1
        }
        company_response = CompanyResponse(**data)
        assert company_response.id == 1
        assert company_response.name == "شرکت تست"
        assert isinstance(company_response.categories, list)
    
    def test_with_categories(self):
        """Test company response with categories"""
        data = {
            "id": 1,
            "name": "شرکت تست",
            "address": "تهران",
            "phone_mobile": "09123456789",
            "latitude": 35.6892,
            "longitude": 51.3890,
            "is_active": True,
            "categories": [
                {"id": 1, "name": "تعمیرات موتور"},
                {"id": 2, "name": "تعویض روغن"}
            ]
        }
        company_response = CompanyResponse(**data)
        assert len(company_response.categories) == 2
        assert company_response.categories[0].name == "تعمیرات موتور"


class TestCategorySchema:
    """Test CategorySchema validation"""
    
    def test_valid_category(self):
        """Test valid category"""
        category = CategorySchema(id=1, name="تعمیرات")
        assert category.id == 1
        assert category.name == "تعمیرات"
    
    def test_required_fields(self):
        """Test required fields"""
        with pytest.raises(ValidationError):
            CategorySchema(id=1)
        
        with pytest.raises(ValidationError):
            CategorySchema(name="تعمیرات")


# ==================== Application Schema Tests ====================

class TestApplicationReviewSchema:
    """Test ApplicationReview schema validation"""
    
    def test_valid_approval(self):
        """Test valid approval"""
        review = ApplicationReview(
            is_approved=True,
            review_notes="تایید شد"
        )
        assert review.is_approved == True
        assert review.review_notes == "تایید شد"
    
    def test_valid_rejection(self):
        """Test valid rejection"""
        review = ApplicationReview(
            is_approved=False,
            review_notes="رد شد"
        )
        assert review.is_approved == False
        assert review.review_notes == "رد شد"
    
    def test_default_review_notes(self):
        """Test default review notes"""
        review = ApplicationReview(is_approved=True)
        assert review.review_notes == ""
    
    def test_review_notes_max_length(self):
        """Test review notes max length"""
        with pytest.raises(ValidationError):
            ApplicationReview(
                is_approved=True,
                review_notes="ت" * 501
            )
    
    def test_required_is_approved(self):
        """Test is_approved is required"""
        with pytest.raises(ValidationError):
            ApplicationReview(review_notes="تست")


class TestApplicationResponseSchema:
    """Test ApplicationResponse schema validation"""
    
    def test_valid_application_response(self):
        """Test valid application response"""
        data = {
            "id": 1,
            "company_name": "شرکت تست",
            "representative_first_name": "علی",
            "representative_last_name": "احمدی",
            "address": "تهران",
            "phone_mobile": "09123456789",
            "service_domain": "تعمیرات",
            "latitude": 35.6892,
            "longitude": 51.3890,
            "status": "pending"
        }
        application = ApplicationResponse(**data)
        assert application.id == 1
        assert application.company_name == "شرکت تست"
        assert application.status == "pending"
    
    def test_optional_fields(self):
        """Test optional fields"""
        data = {
            "id": 1,
            "company_name": "شرکت تست",
            "representative_first_name": "علی",
            "representative_last_name": "احمدی",
            "address": "تهران",
            "phone_mobile": "09123456789",
            "service_domain": "تعمیرات",
            "latitude": 35.6892,
            "longitude": 51.3890,
            "status": "pending"
        }
        application = ApplicationResponse(**data)
        assert application.phone_landline is None
        assert application.reviewed_by is None
        assert application.reviewed_at is None


# ==================== Pagination Schema Tests ====================

class TestPaginationParamsSchema:
    """Test PaginationParams schema validation"""
    
    def test_default_values(self):
        """Test default values"""
        params = PaginationParams()
        assert params.page == 1
        assert params.per_page == 20
    
    def test_custom_values(self):
        """Test custom values"""
        params = PaginationParams(page=3, per_page=50)
        assert params.page == 3
        assert params.per_page == 50
    
    def test_page_minimum_constraint(self):
        """Test page minimum value - auto-corrects to 1"""
        params = PaginationParams(page=0)
        assert params.page == 1
        
        params = PaginationParams(page=-5)
        assert params.page == 1
    
    def test_per_page_constraints(self):
        """Test per_page constraints - auto-corrects invalid values"""
        # Minimum - auto-corrects to 1
        params = PaginationParams(per_page=0)
        assert params.per_page == 1
        
        params = PaginationParams(per_page=-5)
        assert params.per_page == 1
        
        # Maximum - auto-corrects to 100
        params = PaginationParams(per_page=150)
        assert params.per_page == 100
    
    def test_offset_calculation(self):
        """Test offset property calculation"""
        params = PaginationParams(page=1, per_page=20)
        assert params.offset == 0
        
        params = PaginationParams(page=2, per_page=20)
        assert params.offset == 20
        
        params = PaginationParams(page=5, per_page=10)
        assert params.offset == 40
    
    def test_limit_property(self):
        """Test limit property"""
        params = PaginationParams(per_page=25)
        assert params.limit == 25


class TestPaginatedResponseSchema:
    """Test PaginatedResponse schema validation"""
    
    def test_create_paginated_response(self):
        """Test create static method"""
        items = [1, 2, 3, 4, 5]
        response = PaginatedResponse.create(
            items=items,
            page=1,
            per_page=5,
            total=25
        )
        
        assert response["success"] == True
        assert response["data"] == items
        assert response["pagination"]["page"] == 1
        assert response["pagination"]["per_page"] == 5
        assert response["pagination"]["total"] == 25
        assert response["pagination"]["total_pages"] == 5
        assert response["pagination"]["has_next"] == True
        assert response["pagination"]["has_prev"] == False
    
    def test_last_page_pagination(self):
        """Test pagination on last page"""
        items = [1, 2, 3]
        response = PaginatedResponse.create(
            items=items,
            page=5,
            per_page=5,
            total=23
        )
        
        assert response["pagination"]["has_next"] == False
        assert response["pagination"]["has_prev"] == True
    
    def test_total_pages_calculation(self):
        """Test total pages calculation"""
        # Exact division
        response = PaginatedResponse.create([], 1, 10, 100)
        assert response["pagination"]["total_pages"] == 10
        
        # With remainder
        response = PaginatedResponse.create([], 1, 10, 95)
        assert response["pagination"]["total_pages"] == 10
        
        response = PaginatedResponse.create([], 1, 10, 91)
        assert response["pagination"]["total_pages"] == 10


# ==================== Response Schema Tests ====================

class TestApiResponseSchema:
    """Test ApiResponse schema validation"""
    
    def test_default_success(self):
        """Test default success value"""
        response = ApiResponse()
        assert response.success == True
        assert response.message is None
        assert response.data is None
    
    def test_with_message_and_data(self):
        """Test with message and data"""
        response = ApiResponse(
            message="عملیات موفق",
            data={"id": 1, "name": "تست"}
        )
        assert response.success == True
        assert response.message == "عملیات موفق"
        assert response.data["id"] == 1
    
    def test_various_data_types(self):
        """Test with various data types"""
        # Dictionary
        response = ApiResponse(data={"key": "value"})
        assert isinstance(response.data, dict)
        
        # List
        response = ApiResponse(data=[1, 2, 3])
        assert isinstance(response.data, list)
        
        # String
        response = ApiResponse(data="test")
        assert isinstance(response.data, str)


class TestErrorResponseSchema:
    """Test ErrorResponse schema validation"""
    
    def test_default_success_false(self):
        """Test default success is False"""
        response = ErrorResponse(error="خطا")
        assert response.success == False
    
    def test_required_error_field(self):
        """Test error field is required"""
        with pytest.raises(ValidationError):
            ErrorResponse()
    
    def test_with_details(self):
        """Test with error details"""
        response = ErrorResponse(
            error="خطای اعتبارسنجی",
            details={"field": "phone", "issue": "فرمت نامعتبر"}
        )
        assert response.error == "خطای اعتبارسنجی"
        assert response.details["field"] == "phone"
    
    def test_without_details(self):
        """Test without details"""
        response = ErrorResponse(error="خطای عمومی")
        assert response.details is None


# ==================== Integration Tests ====================

class TestSchemaIntegration:
    """Test schemas working together"""
    
    def test_company_list_response(self):
        """Test CompanyListResponse with multiple companies"""
        companies = [
            {
                "id": 1,
                "name": "شرکت 1",
                "address": "تهران",
                "phone_mobile": "09123456789",
                "latitude": 35.6892,
                "longitude": 51.3890,
                "is_active": True,
                "categories": []
            },
            {
                "id": 2,
                "name": "شرکت 2",
                "address": "اصفهان",
                "phone_mobile": "09351234567",
                "latitude": 32.6546,
                "longitude": 51.6680,
                "is_active": True,
                "categories": [{"id": 1, "name": "تعمیرات"}]
            }
        ]
        
        response = CompanyListResponse(providers=companies)
        assert len(response.providers) == 2
        assert response.providers[0].name == "شرکت 1"
        assert len(response.providers[1].categories) == 1
    
    def test_application_list_response(self):
        """Test ApplicationListResponse"""
        applications = [
            {
                "id": 1,
                "company_name": "شرکت تست",
                "representative_first_name": "علی",
                "representative_last_name": "احمدی",
                "address": "تهران",
                "phone_mobile": "09123456789",
                "service_domain": "تعمیرات",
                "latitude": 35.6892,
                "longitude": 51.3890,
                "status": "pending"
            }
        ]
        
        response = ApplicationListResponse(applications=applications)
        assert len(response.applications) == 1
        assert response.applications[0].status == "pending"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

