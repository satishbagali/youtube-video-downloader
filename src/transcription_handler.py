"""
Module for handling video transcriptions
"""

import os
import json
from typing import Optional, Dict, Any
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from config.settings import Config

class TranscriptionHandler:
    def __init__(self, output_dir: str):
        """Initialize the transcription handler"""
        self.output_dir = output_dir
        self.transcript_dir = Config.TRANSCRIPTS_DIR
        os.makedirs(self.transcript_dir, exist_ok=True)
        
    def get_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from URL"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get('id')
        except:
            return None

    def format_transcript(self, transcript_list):
        """Format transcript entries into readable text"""
        formatted_lines = []
        for entry in transcript_list:
            start_time = int(entry['start'])
            minutes = start_time // 60
            seconds = start_time % 60
            text = entry.get('text', '')
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            formatted_lines.append(f"{timestamp} {text}")
        return "\n".join(formatted_lines)

    def get_transcription(self, video_url: str, video_title: str) -> bool:
        """
        Get transcription for a video and save it to a file
        
        Args:
            video_url (str): URL of the video
            video_title (str): Title of the video
            
        Returns:
            bool: True if transcription was successful, False otherwise
        """
        try:
            # Get video ID
            video_id = self.get_video_id(video_url)
            if not video_id:
                print(f"Could not extract video ID from URL: {video_url}")
                return False

            # Get transcript
            print(f"\nGetting transcription for: {video_title}")
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            except NoTranscriptFound:
                print(f"No transcripts found for video: {video_title}")
                return False
            except TranscriptsDisabled:
                print(f"Transcripts are disabled for video: {video_title}")
                return False
            
            if not transcript_list:
                print(f"No transcript content available for video: {video_title}")
                return False
            
            # Format transcript using our custom formatter
            formatted_transcript = self.format_transcript(transcript_list)
            
            # Create transcript file
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            transcript_file = os.path.join(self.transcript_dir, f"{safe_title}.txt")
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"Title: {video_title}\n")
                f.write(f"URL: {video_url}\n")
                f.write("\n\n")
                # Write transcript
                f.write(formatted_transcript)
            
            print(f"Transcription saved to: {transcript_file}")
            return True
            
        except Exception as e:
            print(f"Error getting transcription: {str(e)}")
            return False

    def get_multiple_transcriptions(self, videos: list) -> list:
        """
        Get transcriptions for multiple videos
        
        Args:
            videos (list): List of dictionaries containing video information
            
        Returns:
            list: List of booleans indicating success/failure for each video
        """
        results = []
        total_videos = len(videos)
        
        for idx, video in enumerate(videos, 1):
            print(f"\nProcessing transcription {idx}/{total_videos}")
            success = self.get_transcription(video['url'], video['title'])
            results.append(success)
            
        return results 