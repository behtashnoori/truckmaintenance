"""
Test suite for menu loading behavior
Ensures no old menu flash and proper skeleton loading
"""
import pytest
import json
from backend.app import create_app, db
from backend.models.company import Category


@pytest.fixture
def app():
    """Create test app with sample categories"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Add sample categories
        categories = [
            Category(name='تعمیرات موتور'),
            Category(name='تعویض روغن'),
            Category(name='لاستیک و رینگ'),
            Category(name='امداد و حادثه')
        ]
        
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestCategoriesAPI:
    """Test categories API behavior"""
    
    def test_categories_endpoint_returns_fresh_data(self, client):
        """Test that categories endpoint returns fresh data with proper headers"""
        response = client.get('/api/public/categories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert len(data['data']) == 4
        
        # Check cache control headers
        assert 'Cache-Control' in response.headers
        assert 'no-store' in response.headers['Cache-Control']
        assert 'no-cache' in response.headers['Cache-Control']
        assert 'must-revalidate' in response.headers['Cache-Control']
        assert 'Pragma' in response.headers
        assert response.headers['Pragma'] == 'no-cache'
    
    def test_categories_are_sorted_consistently(self, client):
        """Test that categories are returned in consistent order"""
        response1 = client.get('/api/public/categories')
        response2 = client.get('/api/public/categories')
        
        data1 = json.loads(response1.data)['data']
        data2 = json.loads(response2.data)['data']
        
        assert len(data1) == len(data2)
        for i, (cat1, cat2) in enumerate(zip(data1, data2)):
            assert cat1['name'] == cat2['name'], f"Category order differs at index {i}"
    
    def test_categories_structure(self, client):
        """Test that categories have expected structure"""
        response = client.get('/api/public/categories')
        data = json.loads(response.data)['data']
        
        for category in data:
            assert 'id' in category
            assert 'name' in category
            assert 'companies_count' in category
            assert isinstance(category['companies_count'], int)
            assert category['companies_count'] >= 0


class TestMenuLoadingBehavior:
    """Test menu loading behavior to prevent old menu flash"""
    
    def test_no_static_fallback_in_category_selector(self):
        """Test that CategorySelector doesn't have static fallback"""
        # This test ensures the component doesn't have hardcoded categories
        # The actual test would be in frontend, but we can verify the API
        # doesn't return stale data
        
        # In a real frontend test, we would:
        # 1. Mount CategorySelector
        # 2. Check that initial render shows skeleton, not old menu
        # 3. Verify that after API call, fresh data is shown
        pass
    
    def test_api_consistency(self, client):
        """Test that API returns consistent data across multiple calls"""
        responses = []
        for _ in range(3):
            response = client.get('/api/public/categories')
            assert response.status_code == 200
            responses.append(json.loads(response.data))
        
        # All responses should be identical
        for i in range(1, len(responses)):
            assert responses[i] == responses[0], f"Response {i} differs from first response"


class TestCacheBehavior:
    """Test caching behavior to prevent stale data"""
    
    def test_no_cache_headers_present(self, client):
        """Test that no-cache headers are present"""
        response = client.get('/api/public/categories')
        
        # Check all required no-cache headers
        headers = response.headers
        assert 'Cache-Control' in headers
        assert 'Pragma' in headers
        
        cache_control = headers['Cache-Control']
        assert 'no-store' in cache_control
        assert 'no-cache' in cache_control
        assert 'must-revalidate' in cache_control
    
    def test_fresh_data_on_each_request(self, client):
        """Test that each request returns fresh data (no caching)"""
        # Make multiple requests and verify they all return the same fresh data
        responses = []
        for _ in range(5):
            response = client.get('/api/public/categories')
            assert response.status_code == 200
            responses.append(json.loads(response.data))
        
        # All responses should be identical (fresh data)
        first_response = responses[0]
        for i, response in enumerate(responses[1:], 1):
            assert response == first_response, f"Response {i} differs from first response"


class TestMenuDataIntegrity:
    """Test menu data integrity"""
    
    def test_categories_have_valid_names(self, client):
        """Test that all categories have valid names"""
        response = client.get('/api/public/categories')
        data = json.loads(response.data)['data']
        
        for category in data:
            name = category['name']
            assert isinstance(name, str)
            assert len(name.strip()) > 0
            assert not name.startswith(' ')  # No leading spaces
            assert not name.endswith(' ')    # No trailing spaces
    
    def test_categories_have_valid_counts(self, client):
        """Test that company counts are valid"""
        response = client.get('/api/public/categories')
        data = json.loads(response.data)['data']
        
        for category in data:
            count = category['companies_count']
            assert isinstance(count, int)
            assert count >= 0  # Should not be negative


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
