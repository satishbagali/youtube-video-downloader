"""
Configuration settings for the YouTube Video Downloader
"""

import os
from dotenv import load_dotenv

class Config:
    # Initialize with default values
    YOUTUBE_API_KEY = None
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    # Base directory is the project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Directory for downloaded videos
    DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
    
    # Directory for transcriptions
    TRANSCRIPTS_DIR = os.path.join(BASE_DIR, 'transcripts')

    @classmethod
    def load_config(cls):
        """Load configuration from environment variables"""
        # Load environment variables from .env file
        load_dotenv(override=True)
        
        # Load API key from environment
        cls.YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
        
        # Create necessary directories
        os.makedirs(cls.DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPTS_DIR, exist_ok=True)
        
        # Validate configuration
        cls.validate_config()

    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.YOUTUBE_API_KEY:
            raise ValueError("YouTube API key not found in environment variables")
        print(f"Using API key: {cls.YOUTUBE_API_KEY[:5]}...") 