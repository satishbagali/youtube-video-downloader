"""
Module for downloading YouTube videos
"""

import os
import time
import yt_dlp
from config.settings import Config
from typing import Optional, Dict, Any

class VideoDownloader:
    def __init__(self, output_dir: str = "downloads"):
        """Initialize the video downloader"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure yt-dlp options with additional settings to handle restrictions
        self.ydl_opts = {
            'format': 'best',  # Download best quality
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            # Add cookies from browser to bypass restrictions
            'cookiesfrombrowser': ('chrome',),  
            # Use multiple external downloaders
            'external_downloader_args': ['--max-download-attempts', '5'],
            # Additional options to bypass restrictions
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_color': True,
            # HTTP/Network options
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'retry_sleep_functions': {'http': lambda n: 5 * n},  # Exponential backoff
            # Use multiple user agents
            'random_user_agent': True,
        }

    def download_video(self, video_url: str) -> bool:
        """
        Download a video from the given URL.
        
        Args:
            video_url (str): The URL of the video to download
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        max_attempts = 3
        current_attempt = 0
        
        while current_attempt < max_attempts:
            try:
                print("\nGetting video information...")
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    # Extract video information first
                    info = ydl.extract_info(video_url, download=False)
                    if not info:
                        raise Exception("Could not extract video information")
                    
                    print(f"Video Title: {info.get('title', 'Unknown')}")
                    print(f"Duration: {info.get('duration', 'Unknown')} seconds")
                    
                    print("Starting download...")
                    # Attempt the actual download
                    ydl.download([video_url])
                    return True
                    
            except Exception as e:
                current_attempt += 1
                print(f"\nAttempt {current_attempt} failed: {str(e)}")
                if current_attempt < max_attempts:
                    print(f"Retrying in 2 seconds...")
                    time.sleep(2)
                    # Try with different format on retry
                    self.ydl_opts['format'] = 'best[height<=720]' if current_attempt == 1 else 'worst'
                else:
                    print(f"Failed to download video after {max_attempts} attempts")
                    return False
        
        return False

    def download_multiple_videos(self, video_urls):
        """
        Download multiple videos
        Returns: List of paths to downloaded video files
        """
        downloaded_paths = []
        total_videos = len(video_urls)
        
        for idx, url in enumerate(video_urls, 1):
            print(f"\nDownloading video {idx}/{total_videos}")
            path = self.download_video(url)
            if path:
                downloaded_paths.append(path)
            else:
                print(f"Failed to download video {idx}")
                
        return downloaded_paths 