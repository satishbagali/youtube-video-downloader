"""
Main application entry point for YouTube Channel Manager
"""

import os
from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from config.settings import Config

def display_welcome_message():
    print("\n=== YouTube Channel Video Manager ===")
    print("This program allows you to:")
    print("1. List all videos from a YouTube channel")
    print("2. Download specific videos or all videos")
    print("3. Get video transcriptions (coming soon)")
    print("=====================================\n")

def main():
    display_welcome_message()
    
    youtube_api = YouTubeAPI()
    downloader = VideoDownloader()

    # Get channel URL from user
    channel_url = input("Please enter the YouTube channel URL: ").strip()
    
    # Get channel ID
    print("\nFetching channel information...")
    channel_id = youtube_api.get_channel_id(channel_url)
    
    if not channel_id:
        print("Error: Could not find channel ID. Please check the URL and try again.")
        return

    # Fetch videos
    print("Fetching videos from channel...")
    videos = youtube_api.get_channel_videos(channel_id)

    if not videos:
        print("No videos found or an error occurred.")
        return

    # Display available videos
    print(f"\nFound {len(videos)} videos:")
    for idx, video in enumerate(videos, 1):
        print(f"\n{idx}. {video['title']}")
        print(f"   URL: {video['url']}")

    # Get user selection
    while True:
        print("\nEnter video number to download (or 'all' for all videos, 'q' to quit):")
        choice = input().strip().lower()
        
        if choice == 'q':
            return
            
        if choice == 'all':
            print(f"\nPreparing to download all {len(videos)} videos...")
            video_urls = [video['url'] for video in videos]
            downloaded_files = downloader.download_multiple_videos(video_urls)
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(videos):
                    print(f"\nPreparing to download: {videos[idx]['title']}")
                    downloaded_files = [downloader.download_video(videos[idx]['url'])]
                    break
                else:
                    print("Invalid selection! Please try again.")
            except ValueError:
                print("Invalid input! Please enter a number or 'all'.")

    # Summary
    if downloaded_files:
        successful_downloads = len([f for f in downloaded_files if f is not None])
        print(f"\nDownload Summary:")
        print(f"Successfully downloaded: {successful_downloads} videos")
        print(f"Failed downloads: {len(videos) if choice == 'all' else 1 - successful_downloads}")
        if successful_downloads > 0:
            print(f"\nVideos are saved in the '{os.path.abspath(Config.DOWNLOAD_DIR)}' directory.")

if __name__ == "__main__":
    main() 