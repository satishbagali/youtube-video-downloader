"""
Test configuration integration
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch
from src.config import Config

@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test"""
    original_env = dict(os.environ)
    os.environ.clear()
    Config.reset()  # Reset singleton instance
    yield
    os.environ.clear()
    os.environ.update(original_env)
    Config.reset()  # Reset singleton instance

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing"""
    temp_path = tmp_path / 'test_dir'
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path

@pytest.fixture
def config_instance(temp_dir):
    """Get a fresh Config instance with clean environment"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    return Config()

def test_singleton_pattern(temp_dir):
    """Test that Config maintains singleton pattern"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    first_instance = Config()
    second_instance = Config()
    assert first_instance is second_instance

def test_initialization_state():
    """Test that Config properly tracks initialization state"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = '/tmp'
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    # First initialization
    config = Config()
    
    # Create a new instance - should not reinitialize
    config2 = Config()
    assert config is config2  # Should be the same instance
    
    # Reset and create new instance - should initialize
    Config.reset()
    config3 = Config()
    assert config is not config3  # Should be a different instance

def test_missing_api_key(temp_dir):
    """Test handling of missing API key"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = str(temp_dir)
    # Deliberately not setting YOUTUBE_API_KEY
    with pytest.raises(ValueError, match="YouTube API key not found in environment variables"):
        Config()

def test_directory_creation(config_instance, temp_dir):
    """Test directory creation"""
    downloads_dir = config_instance.get_downloads_dir()
    transcripts_dir = config_instance.get_transcripts_dir()
    
    assert downloads_dir.exists()
    assert transcripts_dir.exists()
    assert downloads_dir.is_dir()
    assert transcripts_dir.is_dir()

def test_directory_paths(temp_dir):
    """Test directory path resolution"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    config = Config()
    
    assert config.get_downloads_dir().resolve() == (temp_dir / 'downloads').resolve()
    assert config.get_transcripts_dir().resolve() == (temp_dir / 'transcripts').resolve()

def test_credentials_path(config_instance, temp_dir):
    """Test credentials path resolution"""
    expected_path = temp_dir / 'credentials.json'
    assert config_instance.get_credentials_path().resolve() == expected_path.resolve()

def test_custom_credentials_path(temp_dir):
    """Test custom credentials path from environment variable"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    custom_path = temp_dir / 'custom' / 'creds.json'
    os.environ['CREDENTIALS_PATH'] = str(custom_path)
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    config = Config()
    assert config.get_credentials_path().resolve() == custom_path.resolve()

@pytest.mark.parametrize('env_var,default_path', [
    ('DOWNLOAD_DIR', 'downloads'),
    ('TRANSCRIPT_DIR', 'transcripts'),
])
def test_custom_directory_paths(temp_dir, env_var, default_path):
    """Test custom directory paths from environment variables"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    custom_path = temp_dir / 'custom' / default_path
    os.environ[env_var] = str(custom_path)
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    config = Config()
    if env_var == 'DOWNLOAD_DIR':
        assert config.get_downloads_dir().resolve() == custom_path.resolve()
    else:
        assert config.get_transcripts_dir().resolve() == custom_path.resolve()

def test_directory_creation_permission_error(config_instance, temp_dir):
    """Test handling of permission errors during directory creation"""
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        mock_mkdir.side_effect = PermissionError("Permission denied")
        with pytest.raises(PermissionError, match="Permission denied creating directory"):
            config_instance._ensure_directory_exists(temp_dir / 'test_dir')

def test_api_constants(temp_dir):
    """Test API service constants"""
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = str(temp_dir)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    config = Config()
    assert config.YOUTUBE_API_SERVICE_NAME == "youtube"
    assert config.YOUTUBE_API_VERSION == "v3"

def test_missing_base_dir():
    """Test handling of missing BASE_DIR environment variable"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    with pytest.raises(ValueError, match="BASE_DIR not found in environment variables"):
        Config()

def test_invalid_directory_path():
    """Test handling of invalid directory paths"""
    Config.reset()
    os.environ.clear()  # Clear all environment variables
    os.environ['BASE_DIR'] = '/nonexistent/path/that/should/not/exist'
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    with pytest.raises(PermissionError, match="Invalid base directory path"):
        Config()

def test_get_base_dir(clean_env, tmp_path):
    """Test that get_base_dir returns the correct base directory path."""
    # Set up
    os.environ['BASE_DIR'] = str(tmp_path)
    os.environ['YOUTUBE_API_KEY'] = 'dummy_key'
    
    # Test
    config = Config()
    assert config.get_base_dir() == tmp_path
    assert config.get_base_dir().exists()
    assert config.get_base_dir().is_dir() 