"""
Configuration management for the YouTube video downloader.
Handles API keys, directory paths, and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration singleton for managing application settings."""
    
    _instance = None
    _initialized = False
    
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Load environment variables only if they haven't been set
        if not os.getenv('YOUTUBE_API_KEY') and not os.getenv('BASE_DIR'):
            load_dotenv()
        
        # Validate API key first before any directory operations
        self._api_key = self._validate_api_key()
        
        # Validate and set base directory
        self._base_dir = self._validate_base_dir()
        
        # Initialize directory paths
        self._downloads_dir = self._resolve_directory('DOWNLOAD_DIR', 'downloads')
        self._transcripts_dir = self._resolve_directory('TRANSCRIPT_DIR', 'transcripts')
        self._credentials_path = self._resolve_credentials_path()
        
        # Create necessary directories
        self._ensure_directory_exists(self._downloads_dir)
        self._ensure_directory_exists(self._transcripts_dir)
        
        self._initialized = True
    
    def _validate_api_key(self):
        """Validate and return the YouTube API key."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YouTube API key not found in environment variables")
        return api_key
    
    def _validate_base_dir(self):
        """Validate and return the base directory path."""
        base_dir_str = os.getenv('BASE_DIR')
        if not base_dir_str:
            raise ValueError("BASE_DIR not found in environment variables")
        
        base_dir = Path(base_dir_str).resolve()
        
        # Check if base directory exists or can be created
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            raise PermissionError("Invalid base directory path")
            
        if not base_dir.is_dir():
            raise ValueError(f"Base directory {base_dir} is not a directory")
            
        return base_dir
    
    def _resolve_directory(self, env_var, default_subdir):
        """Resolve directory path from environment variable or default."""
        custom_path = os.getenv(env_var)
        if custom_path:
            path = Path(custom_path)
            # If path is relative, make it relative to base_dir
            return path if path.is_absolute() else (self._base_dir / custom_path).resolve()
        return (self._base_dir / default_subdir).resolve()
    
    def _resolve_credentials_path(self):
        """Resolve credentials file path."""
        custom_path = os.getenv('CREDENTIALS_PATH')
        if custom_path:
            path = Path(custom_path)
            # If path is relative, make it relative to base_dir
            return path if path.is_absolute() else (self._base_dir / custom_path).resolve()
        return (self._base_dir / 'credentials.json').resolve()
    
    def _ensure_directory_exists(self, path):
        """Ensure directory exists, creating it if necessary."""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Permission denied creating directory {path}: {e}")
        except OSError as e:
            raise OSError(f"Error creating directory {path}: {e}")
    
    def get_api_key(self):
        """Get the YouTube API key."""
        return self._api_key
    
    def get_base_dir(self):
        """Get the base directory path."""
        return self._base_dir
    
    def get_downloads_dir(self):
        """Get the downloads directory path."""
        return self._downloads_dir
    
    def get_transcripts_dir(self):
        """Get the transcripts directory path."""
        return self._transcripts_dir
    
    def get_credentials_path(self):
        """Get the credentials file path."""
        return self._credentials_path
    
    def __setattr__(self, name, value):
        """Prevent modification of critical attributes after initialization."""
        if self._initialized and name in {
            '_api_key', '_base_dir', '_downloads_dir',
            '_transcripts_dir', '_credentials_path'
        }:
            raise AttributeError(f"Cannot modify {name} after initialization")
        super().__setattr__(name, value)
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance for testing."""
        cls._instance = None
        cls._initialized = False
        # Clear environment variables in test environment
        if 'PYTEST_CURRENT_TEST' in os.environ:
            keep_vars = {'PYTEST_CURRENT_TEST', 'PATH', 'PYTHONPATH'}
            for key in list(os.environ.keys()):
                if key not in keep_vars:
                    del os.environ[key]