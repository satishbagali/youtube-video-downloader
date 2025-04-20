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
    
    return results_dir 