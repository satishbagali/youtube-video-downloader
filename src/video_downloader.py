"""
Module for downloading YouTube videos
"""

import os
import time
import yt_dlp
from config.settings import Config
from typing import Optional, Dict, Any, List

class VideoDownloader:
    def __init__(self, output_dir: str = Config.DOWNLOAD_DIR):
        """Initialize the video downloader"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure yt-dlp options with minimal settings
        self.ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'progress_hooks': [self.progress_hook]
        }

    def progress_hook(self, d):
        """Show download progress"""
        if d['status'] == 'downloading':
            try:
                percent = d['_percent_str']
                speed = d['_speed_str']
                print(f"\rDownloading... {percent} at {speed}", end='', flush=True)
            except:
                pass
        elif d['status'] == 'finished':
            print("\nDownload completed!")

    def download_video(self, video_url: str) -> bool:
        """
        Download a video from the given URL.
        
        Args:
            video_url (str): The URL of the video to download
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            print("\nGetting video information...")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract video information first
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    print("Could not extract video information")
                    return False
                
                print(f"\nVideo Title: {info.get('title', 'Unknown')}")
                print(f"Duration: {info.get('duration', 'Unknown')} seconds")
                
                # Attempt the download
                print("\nStarting download...")
                ydl.download([video_url])
                return True
                
        except Exception as e:
            print(f"\nDownload failed: {str(e)}")
            return False
        
        return False

    def download_multiple_videos(self, video_urls: List[str]) -> List[bool]:
        """
        Download multiple videos
        
        Args:
            video_urls (List[str]): List of video URLs to download
            
        Returns:
            List[bool]: List of booleans indicating success/failure for each video
        """
        results = []
        total_videos = len(video_urls)
        
        for idx, url in enumerate(video_urls, 1):
            print(f"\nDownloading video {idx}/{total_videos}")
            success = self.download_video(url)
            results.append(success)
            if success:
                print(f"Successfully downloaded video {idx}/{total_videos}")
            else:
                print(f"Failed to download video {idx}/{total_videos}")
                
        return results 