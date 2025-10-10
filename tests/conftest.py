"""
Shared pytest configuration and fixtures for all tests.

This file is automatically discovered by pytest and provides
common fixtures and configurations for the entire test suite.
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration constants
BASE_URL = "http://localhost:5000/api"
TEST_TIMEOUT = 30  # seconds


@pytest.fixture(scope="session")
def base_url():
    """Provide base API URL for tests."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_headers():
    """Provide common API headers."""
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="function")
def test_client():
    """
    Provide a test client for API requests.
    Can be customized based on your testing framework.
    """
    # TODO: Implement based on your backend framework
    pass


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "admin: mark test as an admin panel test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically add markers to tests based on their location."""
    for item in items:
        # Add markers based on test file location
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "admin" in str(item.fspath):
            item.add_marker(pytest.mark.admin)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

