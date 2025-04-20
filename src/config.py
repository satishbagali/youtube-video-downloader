"""
Configuration management for the YouTube video downloader.
Handles API keys, directory paths, and environment variables.
Uses singleton pattern to ensure consistent configuration across the application.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import warnings
import shutil

class Config:
    """Configuration class for YouTube video downloader.
    Handles environment variables, paths, and API configuration.
    """
    _instance = None
    _initialized = False

    # API constants
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._load_environment()
        self._base_dir = self._validate_base_dir()
        os.chdir(str(self._base_dir))
        self._api_key = self._validate_api_key()
        self._initialize_directories()
        self._initialized = True

    def _load_environment(self):
        """Load environment variables."""
        # Only load from .env file if not in test mode
        if not os.getenv('TEST_MODE'):
            load_dotenv(override=True)

        # Load environment variables
        self._api_key = os.getenv('YOUTUBE_API_KEY')
        self._base_dir = os.getenv('BASE_DIR', os.getcwd())
        self._downloads_dir = os.getenv('DOWNLOAD_DIR')
        self._transcripts_dir = os.getenv('TRANSCRIPT_DIR')
        self._credentials_path = os.getenv('CREDENTIALS_PATH')

    def _validate_base_dir(self) -> Path:
        """Validate and return the base directory path."""
        base_dir = os.getenv('BASE_DIR')
        if not base_dir:
            raise ValueError("BASE_DIR not found in environment variables")
        
        path = Path(base_dir).resolve()
        try:
            self._ensure_directory_exists(path)
        except OSError as e:
            if "Read-only file system" in str(e):
                raise PermissionError("Invalid base directory path") from e
            raise ValueError(f"Error creating directory {path}: {str(e)}")
        
        return path

    def _validate_api_key(self):
        """Validate that the API key is present and set."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YouTube API key not found in environment variables")
        return api_key

    def _initialize_directories(self):
        """Initialize required directories."""
        self._downloads_dir = self._resolve_directory('DOWNLOAD_DIR', 'downloads')
        self._transcripts_dir = self._resolve_directory('TRANSCRIPT_DIR', 'transcripts')
        self._credentials_path = self._resolve_credentials_path()

    def _resolve_directory(self, env_var, default_path):
        """Resolve directory path from environment variable or default."""
        path = os.getenv(env_var)
        if path:
            dir_path = Path(path).resolve()
        else:
            dir_path = self._base_dir / default_path
        
        self._ensure_directory_exists(dir_path)
        return dir_path

    def _resolve_credentials_path(self):
        """Resolve credentials file path."""
        path = self._credentials_path
        if path:
            return Path(path).resolve()
        return self._base_dir / 'credentials.json'

    def _ensure_directory_exists(self, path: Path):
        """Ensure directory exists, create if it doesn't."""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Permission denied creating directory {path}: {str(e)}")
        except OSError as e:
            raise e  # Let the caller handle specific OSError cases

    @property
    def api_key(self):
        return self._api_key

    @property
    def downloads_dir(self):
        return self._downloads_dir

    @property
    def transcripts_dir(self):
        return self._transcripts_dir

    @property
    def credentials_path(self):
        return self._credentials_path

    @property
    def api_service_name(self):
        return self.YOUTUBE_API_SERVICE_NAME

    @property
    def api_version(self):
        return self.YOUTUBE_API_VERSION

    def get_base_dir(self):
        """Return the base directory path."""
        return self._base_dir

    def get_downloads_dir(self) -> Path:
        """Get the downloads directory path."""
        return self._downloads_dir

    def get_transcripts_dir(self) -> Path:
        """Get the transcripts directory path."""
        return self._transcripts_dir

    def get_credentials_path(self) -> Path:
        """Get the credentials file path."""
        return self._credentials_path

    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None
        cls._initialized = False