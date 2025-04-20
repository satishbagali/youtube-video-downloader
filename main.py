"""
YouTube Video Downloader - Main Script
"""

import os
import sys
from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from src.transcription_handler import TranscriptionHandler
from config.settings import Config

def display_welcome_message():
    """Display welcome message and instructions"""
    print("\n=== YouTube Video Downloader ===")
    print("This program allows you to:")
    print("1. List all videos from a YouTube channel")
    print("2. Download specific videos or all videos")
    print("3. Get video transcriptions")
    print("=====================================\n")

def main():
    """Main program execution"""
    try:
        # Load configuration
        Config.load_config()
        
        display_welcome_message()

        # Initialize components
        youtube_api = YouTubeAPI()
        downloader = VideoDownloader(output_dir=Config.DOWNLOAD_DIR)
        transcriber = TranscriptionHandler(output_dir=Config.DOWNLOAD_DIR)

        while True:
            # Get channel URL from user
            channel_url = input("\nEnter YouTube channel URL (or 'q' to quit): ").strip()
            
            if channel_url.lower() == 'q':
                print("\nThank you for using YouTube Video Downloader!")
                break

            # Get channel ID and videos
            print("\nFetching channel information...")
            channel_id = youtube_api.get_channel_id(channel_url)
            
            if not channel_id:
                print("Error: Could not find channel ID. Please check the URL and try again.")
                continue

            print("Fetching videos from channel...")
            videos = youtube_api.get_channel_videos(channel_id)

            if not videos:
                print("No videos found or an error occurred.")
                continue

            # Display available videos
            print(f"\nFound {len(videos)} videos:")
            for idx, video in enumerate(videos, 1):
                print(f"\n{idx}. {video['title']}")
                print(f"   URL: {video['url']}")

            # Get user selection
            while True:
                print("\nOptions:")
                print("- Enter video number to download a specific video")
                print("- Enter 'all' to download all videos")
                print("- Enter 'b' to go back to channel URL input")
                print("- Enter 'q' to quit")
                
                choice = input("\nYour choice: ").strip().lower()
                
                if choice == 'q':
                    print("\nThank you for using YouTube Video Downloader!")
                    return
                    
                if choice == 'b':
                    break
                    
                if choice == 'all':
                    print(f"\nPreparing to download all {len(videos)} videos...")
                    video_urls = [video['url'] for video in videos]
                    downloaded = downloader.download_multiple_videos(video_urls)
                    
                    # Get transcriptions for successfully downloaded videos
                    print("\nGetting transcriptions for downloaded videos...")
                    transcriber.get_multiple_transcriptions(videos)
                    break
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(videos):
                            print(f"\nPreparing to download: {videos[idx]['title']}")
                            success = downloader.download_video(videos[idx]['url'])
                            if success:
                                print(f"\nVideo downloaded successfully to: {Config.DOWNLOAD_DIR}")
                                # Get transcription for the downloaded video
                                print("\nGetting video transcription...")
                                transcriber.get_transcription(videos[idx]['url'], videos[idx]['title'])
                            else:
                                print("\nFailed to download the video.")
                            break
                        else:
                            print("Invalid selection! Please try again.")
                    except ValueError:
                        print("Invalid input! Please enter a number, 'all', 'b', or 'q'.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nThank you for using YouTube Video Downloader!")

if __name__ == "__main__":
    main() 