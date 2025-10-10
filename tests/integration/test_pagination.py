"""
Comprehensive tests for pagination functionality
Tests both schema validation and route integration
"""
import pytest
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import create_app, db
from backend.models.user import User, Admin
from backend.models.provider_application import ProviderApplication
from backend.models.company import Company, Category
from backend.schemas.pagination import PaginationParams, PaginatedResponse
import jwt
import datetime


@pytest.fixture(scope='module')
def app():
    """Create application for testing (module scope to share database)"""
    import os
    import tempfile
    
    # Create a temporary SQLite file (not in-memory, so it persists)
    db_fd, db_path = tempfile.mkstemp()
    
    # Temporarily override environment variables
    old_db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    os.environ['TESTING'] = 'True'
    
    # Import after setting env vars
    app = create_app()
    
    # Double-check the config is SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-for-pagination-testing'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize db
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.session.close()
        try:
            db.drop_all()
        except Exception:
            pass
        # Close database connections within app context
        db.engine.dispose()
    
    os.close(db_fd)
    # On Windows, we need to wait a bit for file handles to be released
    import time
    time.sleep(0.1)
    try:
        os.unlink(db_path)
    except PermissionError:
        # If file is still locked, that's okay - it will be cleaned up later
        pass
    
    # Restore old environment
    if old_db_uri:
        os.environ['SQLALCHEMY_DATABASE_URI'] = old_db_uri
    else:
        os.environ.pop('SQLALCHEMY_DATABASE_URI', None)
    os.environ.pop('TESTING', None)


@pytest.fixture(scope='module')
def client(app):
    """Create test client (module scope)"""
    return app.test_client()


@pytest.fixture(scope='module')
def admin_user(app):
    """Create admin user for testing (module scope)"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='admin_pagination').first()
        if existing_user:
            return existing_user.id
        
        # Create base user first
        user = User(
            username='admin_pagination',
            email='admin.pagination@test.com',
            full_name='Pagination Admin',
            role='admin',
            is_active=True
        )
        user.set_password('Admin@1234')
        db.session.add(user)
        db.session.flush()
        
        # Create admin record
        admin = Admin(user_id=user.id)
        db.session.add(admin)
        db.session.commit()
        
        # Refresh to get the id
        db.session.refresh(user)
        user_id = user.id
        
    return user_id


@pytest.fixture(scope='module')
def business_expert_user(app):
    """Create business expert user for testing (module scope)"""
    with app.app_context():
        from backend.models.user import BusinessExpert
        
        # Check if user already exists
        existing_user = User.query.filter_by(username='expert_pagination').first()
        if existing_user:
            return existing_user.id
        
        # Create base user first
        user = User(
            username='expert_pagination',
            email='expert.pagination@test.com',
            full_name='Pagination Expert',
            role='business_expert',
            is_active=True
        )
        user.set_password('Expert@1234')
        db.session.add(user)
        db.session.flush()
        
        # Create business expert record
        expert = BusinessExpert(user_id=user.id)
        db.session.add(expert)
        db.session.commit()
        
        db.session.refresh(user)
        user_id = user.id
        
    return user_id


@pytest.fixture(scope='module')
def admin_token(app, admin_user):
    """Generate JWT token for admin (module scope)"""
    with app.app_context():
        admin = db.session.get(User, admin_user)  # Use db.session.get instead of query.get
        token = jwt.encode({
            'user_id': admin.id,
            'username': admin.username,
            'role': admin.role,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token


@pytest.fixture(scope='module')
def expert_token(app, business_expert_user):
    """Generate JWT token for business expert (module scope)"""
    with app.app_context():
        expert = db.session.get(User, business_expert_user)  # Use db.session.get instead of query.get
        token = jwt.encode({
            'user_id': expert.id,
            'username': expert.username,
            'role': expert.role,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token


class TestPaginationParams:
    """Test PaginationParams schema validation"""
    
    def test_default_values(self):
        """Test default pagination values"""
        pagination = PaginationParams()
        assert pagination.page == 1
        assert pagination.per_page == 20
    
    def test_custom_values(self):
        """Test custom pagination values"""
        pagination = PaginationParams(page=5, per_page=50)
        assert pagination.page == 5
        assert pagination.per_page == 50
    
    def test_negative_page_normalized_to_one(self):
        """Test negative page is normalized to 1"""
        pagination = PaginationParams(page=-5)
        assert pagination.page == 1
    
    def test_zero_page_normalized_to_one(self):
        """Test zero page is normalized to 1"""
        pagination = PaginationParams(page=0)
        assert pagination.page == 1
    
    def test_negative_per_page_normalized_to_one(self):
        """Test negative per_page is normalized to 1"""
        pagination = PaginationParams(per_page=-10)
        assert pagination.per_page == 1
    
    def test_zero_per_page_normalized_to_one(self):
        """Test zero per_page is normalized to 1"""
        pagination = PaginationParams(per_page=0)
        assert pagination.per_page == 1
    
    def test_per_page_exceeds_max_limited_to_100(self):
        """Test per_page > 100 is limited to 100"""
        pagination = PaginationParams(per_page=500)
        assert pagination.per_page == 100
    
    def test_per_page_max_boundary(self):
        """Test per_page at max boundary (100)"""
        pagination = PaginationParams(per_page=100)
        assert pagination.per_page == 100
    
    def test_offset_calculation_first_page(self):
        """Test offset calculation for first page"""
        pagination = PaginationParams(page=1, per_page=20)
        assert pagination.offset == 0
    
    def test_offset_calculation_second_page(self):
        """Test offset calculation for second page"""
        pagination = PaginationParams(page=2, per_page=20)
        assert pagination.offset == 20
    
    def test_offset_calculation_various_pages(self):
        """Test offset calculation for various pages"""
        test_cases = [
            (1, 10, 0),
            (2, 10, 10),
            (3, 10, 20),
            (5, 25, 100),
            (10, 50, 450),
        ]
        for page, per_page, expected_offset in test_cases:
            pagination = PaginationParams(page=page, per_page=per_page)
            assert pagination.offset == expected_offset, \
                f"Page {page}, per_page {per_page}: expected offset {expected_offset}, got {pagination.offset}"
    
    def test_limit_property(self):
        """Test limit property returns per_page"""
        pagination = PaginationParams(page=1, per_page=30)
        assert pagination.limit == 30


class TestPaginatedResponse:
    """Test PaginatedResponse schema"""
    
    def test_create_first_page_with_more_pages(self):
        """Test creating response for first page when more pages exist"""
        items = [{"id": i} for i in range(20)]
        response = PaginatedResponse.create(
            items=items,
            page=1,
            per_page=20,
            total=100
        )
        
        assert response["success"] is True
        assert len(response["data"]) == 20
        assert response["pagination"]["page"] == 1
        assert response["pagination"]["per_page"] == 20
        assert response["pagination"]["total"] == 100
        assert response["pagination"]["total_pages"] == 5
        assert response["pagination"]["has_next"] is True
        assert response["pagination"]["has_prev"] is False
    
    def test_create_middle_page(self):
        """Test creating response for a middle page"""
        items = [{"id": i} for i in range(20)]
        response = PaginatedResponse.create(
            items=items,
            page=3,
            per_page=20,
            total=100
        )
        
        assert response["pagination"]["page"] == 3
        assert response["pagination"]["has_next"] is True
        assert response["pagination"]["has_prev"] is True
    
    def test_create_last_page(self):
        """Test creating response for last page"""
        items = [{"id": i} for i in range(10)]
        response = PaginatedResponse.create(
            items=items,
            page=5,
            per_page=20,
            total=90
        )
        
        assert response["pagination"]["page"] == 5
        assert response["pagination"]["total_pages"] == 5
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is True
    
    def test_create_single_page(self):
        """Test creating response when all items fit in one page"""
        items = [{"id": i} for i in range(10)]
        response = PaginatedResponse.create(
            items=items,
            page=1,
            per_page=20,
            total=10
        )
        
        assert response["pagination"]["total_pages"] == 1
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is False
    
    def test_create_empty_results(self):
        """Test creating response with no items"""
        response = PaginatedResponse.create(
            items=[],
            page=1,
            per_page=20,
            total=0
        )
        
        assert len(response["data"]) == 0
        assert response["pagination"]["total"] == 0
        assert response["pagination"]["total_pages"] == 0
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is False
    
    def test_create_total_pages_calculation(self):
        """Test total_pages calculation for various totals"""
        test_cases = [
            (0, 20, 0),    # No items
            (1, 20, 1),    # One item
            (20, 20, 1),   # Exactly one page
            (21, 20, 2),   # One item over
            (40, 20, 2),   # Exactly two pages
            (99, 20, 5),   # 99 items, 20 per page
            (100, 20, 5),  # 100 items, 20 per page
        ]
        
        for total, per_page, expected_pages in test_cases:
            response = PaginatedResponse.create(
                items=[],
                page=1,
                per_page=per_page,
                total=total
            )
            assert response["pagination"]["total_pages"] == expected_pages, \
                f"Total {total}, per_page {per_page}: expected {expected_pages} pages, got {response['pagination']['total_pages']}"


class TestUsersPagination:
    """Test pagination in /api/users endpoint"""
    
    def test_routes_registered(self, app):
        """Test that routes are registered"""
        with app.app_context():
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            assert any('/api/users' in route for route in routes), "Users route not found"
    
    def test_admin_token_valid(self, app, admin_user, admin_token):
        """Test that admin token is valid"""
        with app.app_context():
            user = db.session.get(User, admin_user)
            assert user is not None, "Admin user not found"
            assert admin_token is not None, "Admin token not generated"
    
    def test_users_api_request(self, client, app, admin_token):
        """Test simple API request to users endpoint"""
        print(f"Token: {admin_token[:50]}...")
        response = client.get(
            '/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        assert response.status_code in [200, 401], f"Unexpected status: {response.status_code}"
    
    def test_users_default_pagination(self, client, app, admin_token):
        """Test users list with default pagination"""
        with app.app_context():
            # Create 25 test users
            for i in range(25):
                user = User(
                    username=f'user_{i}',
                    email=f'user{i}@test.com',
                    full_name=f'User {i}',
                    role='support',  # Add role
                    is_active=True
                )
                user.set_password('Test@1234')
                db.session.add(user)
            db.session.commit()
        
        response = client.get(
            '/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 20
        assert len(data["data"]) == 20
        assert data["pagination"]["total"] >= 25
    
    def test_users_custom_page_size(self, client, app, admin_token):
        """Test users list with custom page size"""
        with app.app_context():
            # Create 15 test users
            for i in range(15):
                user = User(
                    username=f'customuser_{i}',
                    email=f'customuser{i}@test.com',
                    full_name=f'Custom User {i}',
                    role='support',
                    is_active=True
                )
                user.set_password('Test@1234')
                db.session.add(user)
            db.session.commit()
        
        response = client.get(
            '/api/users?per_page=10',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["per_page"] == 10
        assert len(data["data"]) == 10
    
    def test_users_second_page(self, client, app, admin_token):
        """Test users list second page"""
        with app.app_context():
            # Create 25 test users
            for i in range(25):
                user = User(
                    username=f'pageuser_{i}',
                    email=f'pageuser{i}@test.com',
                    full_name=f'Page User {i}',
                    role='support',
                    is_active=True
                )
                user.set_password('Test@1234')
                db.session.add(user)
            db.session.commit()
        
        response = client.get(
            '/api/users?page=2&per_page=10',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_prev"] is True
    
    def test_users_invalid_page_normalized(self, client, app, admin_token):
        """Test users list with invalid page number"""
        response = client.get(
            '/api/users?page=-1',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Debug: print response if failed
        if response.status_code != 200:
            print(f"Response: {response.get_json()}")
        
        assert response.status_code == 200
        data = response.get_json()
        # Should be normalized to page 1
        assert data["pagination"]["page"] == 1
    
    def test_users_excessive_per_page_limited(self, client, app, admin_token):
        """Test users list with excessive per_page value"""
        response = client.get(
            '/api/users?per_page=500',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Should be limited to 100
        assert data["pagination"]["per_page"] == 100


class TestApplicationsPagination:
    """Test pagination in /api/admin/applications endpoint"""
    
    def test_applications_default_pagination(self, client, app, admin_token):
        """Test applications list with default pagination"""
        with app.app_context():
            # Create 25 test applications
            for i in range(25):
                application = ProviderApplication(
                    company_name=f'Company {i}',
                    representative_first_name=f'First{i}',
                    representative_last_name=f'Last{i}',
                    phone_mobile=f'0912345{i:04d}',
                    address=f'Address {i}',
                    service_domain='تعمیرات',
                    latitude=35.6892,
                    longitude=51.3890
                )
                db.session.add(application)
            db.session.commit()
        
        response = client.get(
            '/api/applications',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 20
        assert len(data["data"]) == 20
    
    def test_applications_with_status_filter(self, client, app, admin_token):
        """Test applications list with status filter and pagination"""
        with app.app_context():
            # Create 15 pending and 10 approved applications
            for i in range(15):
                application = ProviderApplication(
                    company_name=f'Pending Company {i}',
                    representative_first_name=f'First{i}',
                    representative_last_name=f'Last{i}',
                    phone_mobile=f'0913345{i:04d}',
                    address=f'Address {i}',
                    service_domain='تعمیرات',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_approved=None
                )
                db.session.add(application)
            
            for i in range(10):
                application = ProviderApplication(
                    company_name=f'Approved Company {i}',
                    representative_first_name=f'First{i}',
                    representative_last_name=f'Last{i}',
                    phone_mobile=f'0914345{i:04d}',
                    address=f'Address {i}',
                    service_domain='تعمیرات',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_approved=True
                )
                db.session.add(application)
            db.session.commit()
        
        response = client.get(
            '/api/applications?status=pending',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Should have at least 15 pending (may have more from previous tests)
        assert data["pagination"]["total"] >= 15
    
    def test_applications_page_beyond_total(self, client, app, admin_token):
        """Test applications list requesting page beyond total pages"""
        with app.app_context():
            # Create only 5 applications
            for i in range(5):
                application = ProviderApplication(
                    company_name=f'Small Company {i}',
                    representative_first_name=f'First{i}',
                    representative_last_name=f'Last{i}',
                    phone_mobile=f'0915345{i:04d}',
                    address=f'Address {i}',
                    service_domain='تعمیرات',
                    latitude=35.6892,
                    longitude=51.3890
                )
                db.session.add(application)
            db.session.commit()
        
        response = client.get(
            '/api/applications?page=5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Should return empty data for page beyond total
        assert len(data["data"]) == 0
        assert data["pagination"]["page"] == 5


class TestProvidersPagination:
    """Test pagination in /api/business-expert/providers endpoint"""
    
    def test_providers_default_pagination(self, client, app, expert_token):
        """Test providers list with default pagination"""
        with app.app_context():
            # Create a category first
            category = Category(name='تعمیرات موتور')
            db.session.add(category)
            db.session.flush()
            
            # Create 30 test providers
            for i in range(30):
                company = Company(
                    name=f'Provider Company {i}',
                    address=f'Provider Address {i}',
                    phone_mobile=f'0916345{i:04d}',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_active=True,
                    created_by=1
                )
                company.categories.append(category)
                db.session.add(company)
            db.session.commit()
        
        response = client.get(
            '/api/business-expert/providers',
            headers={'Authorization': f'Bearer {expert_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 20
        assert len(data["data"]) == 20
        assert data["pagination"]["total"] == 30
    
    def test_providers_with_filters_and_pagination(self, client, app, expert_token):
        """Test providers list with filters and pagination"""
        with app.app_context():
            category = Category(name='تعمیرات برق')
            db.session.add(category)
            db.session.flush()
            
            # Create 10 active and 5 inactive providers
            for i in range(10):
                company = Company(
                    name=f'Active Provider {i}',
                    address=f'Address {i}',
                    phone_mobile=f'0917345{i:04d}',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_active=True,
                    created_by=1
                )
                company.categories.append(category)
                db.session.add(company)
            
            for i in range(5):
                company = Company(
                    name=f'Inactive Provider {i}',
                    address=f'Address {i}',
                    phone_mobile=f'0918345{i:04d}',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_active=False,
                    created_by=1
                )
                company.categories.append(category)
                db.session.add(company)
            db.session.commit()
        
        response = client.get(
            '/api/business-expert/providers?is_active=true&per_page=5',
            headers={'Authorization': f'Bearer {expert_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["per_page"] == 5
        # Should have at least 10 active providers (may have more from previous tests)
        assert data["pagination"]["total"] >= 10
        assert len(data["data"]) == 5  # per_page is 5
    
    def test_providers_search_with_pagination(self, client, app, expert_token):
        """Test providers list with search and pagination"""
        with app.app_context():
            category = Category(name='تعمیرات')
            db.session.add(category)
            db.session.flush()
            
            # Create providers with specific names
            for i in range(5):
                company = Company(
                    name=f'Special Provider {i}',
                    address=f'Address {i}',
                    phone_mobile=f'0919345{i:04d}',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_active=True,
                    created_by=1
                )
                company.categories.append(category)
                db.session.add(company)
            
            for i in range(10):
                company = Company(
                    name=f'Regular Provider {i}',
                    address=f'Address {i}',
                    phone_mobile=f'0920345{i:04d}',
                    latitude=35.6892,
                    longitude=51.3890,
                    is_active=True,
                    created_by=1
                )
                company.categories.append(category)
                db.session.add(company)
            db.session.commit()
        
        response = client.get(
            '/api/business-expert/providers?search=Special',
            headers={'Authorization': f'Bearer {expert_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["total"] == 5


class TestPaginationEdgeCases:
    """Test edge cases for pagination"""
    
    def test_very_large_page_number(self, client, app, admin_token):
        """Test pagination with very large page number"""
        response = client.get(
            '/api/users?page=999999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Should return empty results
        assert len(data["data"]) == 0
    
    def test_string_page_parameter(self, client, app, admin_token):
        """Test pagination with invalid string page parameter"""
        response = client.get(
            '/api/users?page=abc',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Flask should handle type conversion, defaulting to 1
        assert response.status_code == 200
    
    def test_float_page_parameter(self, client, app, admin_token):
        """Test pagination with float page parameter"""
        response = client.get(
            '/api/users?page=2.5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # Flask may not convert "2.5" to int, defaulting to 1
        assert data["pagination"]["page"] in [1, 2], "Float should be handled gracefully"


class TestPaginationResponseStructure:
    """Test pagination response structure consistency"""
    
    def test_users_response_structure(self, client, app, admin_token):
        """Test users endpoint returns proper pagination structure"""
        response = client.get(
            '/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check required fields
        assert "success" in data
        assert "data" in data
        assert "pagination" in data
        
        # Check pagination fields
        pagination = data["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination
    
    def test_applications_response_structure(self, client, app, admin_token):
        """Test applications endpoint returns proper pagination structure"""
        response = client.get(
            '/api/applications',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check required fields
        assert "success" in data
        assert "data" in data
        assert "pagination" in data
        
        # Check pagination fields
        pagination = data["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination
    
    def test_providers_response_structure(self, client, app, expert_token):
        """Test providers endpoint returns proper pagination structure"""
        response = client.get(
            '/api/business-expert/providers',
            headers={'Authorization': f'Bearer {expert_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check required fields
        assert "success" in data
        assert "data" in data
        assert "pagination" in data
        
        # Check pagination fields
        pagination = data["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

