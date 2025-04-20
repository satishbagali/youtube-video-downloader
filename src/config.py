"""Configuration management module.

This module provides a singleton Config class that manages application settings,
including API keys, directory paths, and environment variables. It ensures
consistent configuration across the application and handles initialization
of required directories.

Example:
    config = Config()
    api_key = config.get_api_key()
    downloads_dir = config.get_downloads_dir()
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Singleton class for managing application configuration.
    
    This class ensures only one instance exists and manages all configuration
    settings, including API keys and directory paths. It handles the loading
    of environment variables and initialization of required directories.
    
    Attributes:
        YOUTUBE_API_SERVICE_NAME (str): Name of the YouTube API service
        YOUTUBE_API_VERSION (str): Version of the YouTube API to use
    """
    
    # Class variables for YouTube API configuration
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    # Singleton instance
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure only one instance of Config exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        """Initialize configuration if not already initialized."""
        if not self._initialized:
            # Load environment variables
            load_dotenv(override=True)
            
            # Get and validate base directory first
            base_dir = os.getenv('BASE_DIR')
            if not base_dir:
                raise ValueError("BASE_DIR not found in environment variables")
            
            self._base_dir = Path(base_dir).resolve()
            if not self._base_dir.exists() and not self._base_dir.parent.exists():
                raise PermissionError("Invalid base directory path")
            
            # Get and validate API key before proceeding with directory setup
            self._api_key = os.getenv('YOUTUBE_API_KEY')
            if not self._api_key:
                raise ValueError("YouTube API key not found in environment variables")
            
            # Set up other directories
            downloads_dir = os.getenv('DOWNLOAD_DIR')
            transcripts_dir = os.getenv('TRANSCRIPT_DIR')
            credentials_path = os.getenv('CREDENTIALS_PATH')
            
            # Resolve paths relative to base directory if not absolute
            if downloads_dir:
                self._downloads_dir = Path(downloads_dir).resolve()
            else:
                self._downloads_dir = (self._base_dir / 'downloads').resolve()
                
            if transcripts_dir:
                self._transcripts_dir = Path(transcripts_dir).resolve()
            else:
                self._transcripts_dir = (self._base_dir / 'transcripts').resolve()
                
            if credentials_path:
                self._credentials_path = Path(credentials_path).resolve()
            else:
                self._credentials_path = (self._base_dir / 'credentials.json').resolve()
            
            # Create necessary directories
            self._ensure_directory_exists(self._base_dir)
            self._ensure_directory_exists(self._downloads_dir)
            self._ensure_directory_exists(self._transcripts_dir)
            
            # Mark as initialized
            self.__class__._initialized = True
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Create directory if it doesn't exist.
        
        Args:
            directory (Path): Directory path to create
            
        Raises:
            PermissionError: If directory cannot be created due to permissions
            OSError: If directory creation fails for other reasons
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Permission denied creating directory: {directory}") from e
        except OSError as e:
            raise OSError(f"Failed to create directory: {directory}") from e
    
    def get_api_key(self) -> str:
        """Get the YouTube API key.
        
        Returns:
            str: The API key
            
        Raises:
            ValueError: If API key is not set
        """
        if not self._api_key:
            raise ValueError("YouTube API key not found in environment variables")
        return self._api_key
    
    def get_downloads_dir(self) -> Path:
        """Get the downloads directory path.
        
        Returns:
            Path: Path to downloads directory
        """
        return self._downloads_dir
    
    def get_transcripts_dir(self) -> Path:
        """Get the transcripts directory path.
        
        Returns:
            Path: Path to transcripts directory
        """
        return self._transcripts_dir
    
    def get_credentials_path(self) -> Path:
        """Get the credentials file path.
        
        Returns:
            Path: Path to credentials file
        """
        return self._credentials_path

    def get_base_dir(self) -> Path:
        """Get the base directory path.
        
        Returns:
            Path: Path to base directory
        """
        return self._base_dir

    def ensure_directories_exist(self):
        """Ensure all required directories exist"""
        self._ensure_directory_exists(self._base_dir)
        self._ensure_directory_exists(self._downloads_dir)
        self._ensure_directory_exists(self._transcripts_dir)
    
    def __setattr__(self, name, value):
        """Prevent modification of critical attributes after initialization"""
        if self._initialized and name.startswith('_'):
            raise AttributeError(f"Cannot modify {name} after initialization")
        super().__setattr__(name, value)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        cls._instance = None
        cls._initialized = False 