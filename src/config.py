"""
Configuration management module
"""
import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration class for managing application settings."""
    
    # Class constants for YouTube API
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    # Class variable for singleton instance
    _instance = None
    _initialized = False

    def __new__(cls):
        """Ensure singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration"""
        if self._initialized:
            return
            
        # Get API key first
        self._api_key = os.getenv('YOUTUBE_API_KEY')
        if not self._api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        # Set up base paths
        base_dir = os.getenv('BASE_DIR')
        if not base_dir:
            raise ValueError("BASE_DIR not found in environment variables")
        
        try:
            base_path = Path(base_dir).resolve()
            if not base_path.exists():
                base_path.mkdir(parents=True, exist_ok=True)
            self._base_dir = base_path
        except (OSError, RuntimeError) as e:
            raise PermissionError(f"Invalid base directory path: {base_dir}") from e
        
        # Set up downloads directory
        downloads_path = os.getenv('DOWNLOAD_DIR')
        if downloads_path:
            try:
                downloads_dir = Path(downloads_path).resolve()
                if not downloads_dir.exists():
                    downloads_dir.mkdir(parents=True, exist_ok=True)
                self._downloads_dir = downloads_dir
            except (OSError, RuntimeError):
                self._downloads_dir = (self._base_dir / 'downloads').resolve()
        else:
            self._downloads_dir = (self._base_dir / 'downloads').resolve()
        self._ensure_directory_exists(self._downloads_dir)
        
        # Set up transcripts directory
        transcripts_path = os.getenv('TRANSCRIPT_DIR')
        if transcripts_path:
            try:
                transcripts_dir = Path(transcripts_path).resolve()
                if not transcripts_dir.exists():
                    transcripts_dir.mkdir(parents=True, exist_ok=True)
                self._transcripts_dir = transcripts_dir
            except (OSError, RuntimeError):
                self._transcripts_dir = (self._base_dir / 'transcripts').resolve()
        else:
            self._transcripts_dir = (self._base_dir / 'transcripts').resolve()
        self._ensure_directory_exists(self._transcripts_dir)
        
        # Set up credentials path
        credentials_path = os.getenv('CREDENTIALS_PATH')
        if credentials_path:
            try:
                creds_path = Path(credentials_path).resolve()
                if not creds_path.parent.exists():
                    creds_path.parent.mkdir(parents=True, exist_ok=True)
                self._credentials_path = creds_path
            except (OSError, RuntimeError):
                self._credentials_path = (self._base_dir / 'credentials.json').resolve()
        else:
            self._credentials_path = (self._base_dir / 'credentials.json').resolve()
        
        self._initialized = True

    def _ensure_directory_exists(self, directory: Path) -> None:
        """
        Ensure that the specified directory exists, creating it if necessary.
        
        Args:
            directory (Path): The directory path to check/create
            
        Raises:
            PermissionError: If directory creation fails due to permissions
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise PermissionError(f"Permission denied creating directory: {directory}") from e

    def get_api_key(self) -> str:
        """Get the YouTube API key."""
        return self._api_key

    def get_downloads_dir(self) -> Path:
        """Get the downloads directory path."""
        return self._downloads_dir

    def get_transcripts_dir(self) -> Path:
        """Get the transcripts directory path."""
        return self._transcripts_dir

    def get_credentials_path(self) -> Path:
        """Get the credentials file path."""
        return self._credentials_path

    def ensure_directories_exist(self):
        """Ensure all required directories exist"""
        self._ensure_directory_exists(self._downloads_dir)
        self._ensure_directory_exists(self._transcripts_dir)
    
    def __setattr__(self, name, value):
        """Prevent modification of critical attributes after initialization"""
        if hasattr(self, '_initialized') and self._initialized and name.startswith('_'):
            raise AttributeError(f"Cannot modify {name} after initialization")
        super().__setattr__(name, value)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        cls._instance = None
        cls._initialized = False 