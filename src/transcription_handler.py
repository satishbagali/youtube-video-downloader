"""
Module for handling video transcriptions
"""

import os
import json
from typing import Optional, Dict, Any, List
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

    def has_captions(self, video_id: str) -> bool:
        """
        Check if a video has available captions
        
        Args:
            video_id (str): The YouTube video ID
            
        Returns:
            bool: True if captions are available, False otherwise
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            return bool(transcript_list.find_manually_created_transcript())
        except Exception:
            return False

    def get_transcript(self, video_id: str, language: str = 'en') -> Optional[List[Dict[str, Any]]]:
        """
        Get transcript for a video in specified language
        
        Args:
            video_id (str): The YouTube video ID
            language (str): Language code (default: 'en')
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of transcript entries or None if not found
        """
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        except Exception:
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

    def save_transcript(self, transcript: List[Dict[str, Any]], file_path: str, include_timestamps: bool = False) -> None:
        """
        Save transcript to a file
        
        Args:
            transcript (List[Dict[str, Any]]): List of transcript entries
            file_path (str): Path to save the transcript
            include_timestamps (bool): Whether to include timestamps in output
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if include_timestamps:
                    f.write(self.format_transcript(transcript))
                else:
                    for entry in transcript:
                        f.write(f"{entry['text']}\n")
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")

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

            # Check if captions are available
            if not self.has_captions(video_id):
                print(f"No captions available for video: {video_title}")
                return False

            # Get transcript
            print(f"\nGetting transcription for: {video_title}")
            transcript_list = self.get_transcript(video_id)
            if not transcript_list:
                print(f"No transcript content available for video: {video_title}")
                return False
            
            # Create transcript file
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            transcript_file = os.path.join(self.transcript_dir, f"{safe_title}.txt")
            
            # Save transcript with timestamps
            self.save_transcript(transcript_list, transcript_file, include_timestamps=True)
            
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