"""
Global pytest configuration and fixtures
"""
import os
import pytest
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def setup_test_results():
    """Ensure test results directory exists before running tests."""
    # Get the project root directory (where pytest.ini is located)
    root_dir = Path(__file__).parent.parent
    
    # Create test results directory if it doesn't exist
    results_dir = root_dir / 'test_results'
    results_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for different types of results
    (results_dir / 'coverage').mkdir(exist_ok=True)
    
    # Ensure we're in test mode
    os.environ['PYTEST_CURRENT_TEST'] = 'True'
    
    return results_dir

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Store original environment variables
    original_env = {}
    for key in ['PYTEST_CURRENT_TEST', 'YOUTUBE_API_KEY', 'BASE_DIR']:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    # Set test environment variables
    os.environ['PYTEST_CURRENT_TEST'] = 'dummy_test'
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    os.environ['BASE_DIR'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    yield
    
    # Restore original environment variables
    for key in ['PYTEST_CURRENT_TEST', 'YOUTUBE_API_KEY', 'BASE_DIR']:
        if key in original_env:
            os.environ[key] = original_env[key]
        elif key in os.environ:
            del os.environ[key] 