"""
Module for handling YouTube API interactions
"""

import re
from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from src.config import Config

class YouTubeAPI:
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the YouTube API client
        
        Args:
            config: Optional Config instance. If not provided, uses the singleton Config.
        """
        self.config = config or Config()
        self.youtube = build('youtube', 'v3', developerKey=self.config.api_key)

    def get_channel_id(self, url: str) -> str:
        """
        Get the channel ID from a YouTube channel URL.
        
        Args:
            url: The YouTube channel URL.
            
        Returns:
            str: The channel ID.
            
        Raises:
            ValueError: If the channel is not found.
        """
        channel_id = self.extract_channel_id(url)
        if channel_id:
            return channel_id

        # For custom URLs and handles, we need to search for the channel
        try:
            # Extract the custom name or handle from the URL
            if '/c/' in url:
                query = url.split('/c/')[-1]
            elif '/@' in url:
                query = url.split('/@')[-1]
            else:
                query = url.split('/user/')[-1]

            # Search for the channel
            request = self.youtube.search().list(
                part="id,snippet",
                q=query,
                type="channel",
                maxResults=1
            )
            response = request.execute()

            if not response.get('items'):
                raise ValueError("Channel not found")

            return response['items'][0]['id']['channelId']
        except HttpError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to get channel ID: {str(e)}")

    def extract_channel_id(self, url: str) -> Optional[str]:
        """
        Extract the channel ID from a YouTube channel URL if it's in the URL.
        
        Args:
            url: The YouTube channel URL.
            
        Returns:
            Optional[str]: The channel ID if found in the URL, None otherwise.
        """
        channel_pattern = r'youtube\.com/channel/(UC[\w-]+)'
        match = re.search(channel_pattern, url)
        return match.group(1) if match else None

    def is_valid_video_url(self, url: str) -> bool:
        """
        Check if a URL is a valid YouTube video URL.
        
        Args:
            url: The URL to check.
            
        Returns:
            bool: True if the URL is a valid YouTube video URL, False otherwise.
        """
        video_patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+'
        ]
        return any(re.search(pattern, url) for pattern in video_patterns)

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get videos from a YouTube channel.
        
        Args:
            channel_id: The channel ID.
            max_results: Maximum number of videos to return.
            
        Returns:
            List[Dict]: List of video information dictionaries.
            
        Raises:
            HttpError: If the API request fails.
        """
        videos = []
        next_page_token = None

        try:
            while len(videos) < max_results:
                request = self.youtube.search().list(
                    part="id,snippet",
                    channelId=channel_id,
                    maxResults=min(50, max_results - len(videos)),
                    type="video",
                    order="date",
                    pageToken=next_page_token
                )
                response = request.execute()

                for item in response['items']:
                    video = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt']
                    }
                    videos.append(video)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            return videos[:max_results]
        except HttpError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to get channel videos: {str(e)}")

    def get_channel_videos_old(self, channel_id):
        """
        Fetch all videos from a channel
        Returns: List of dictionaries containing video details
        """
        try:
            videos = []
            next_page_token = None

            while True:
                request = self.youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=50,
                    order="date",
                    type="video",
                    pageToken=next_page_token
                )
                response = request.execute()

                for item in response['items']:
                    video = {
                        'title': item['snippet']['title'],
                        'video_id': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    videos.append(video)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            return videos

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def get_channel_video_ids(self, channel_url: str, max_results: int = 50) -> List[str]:
        """
        Get video IDs from a YouTube channel URL.
        
        This method first extracts the channel ID from the URL, then retrieves
        the most recent videos from that channel. The videos are returned in
        chronological order (newest first).
        
        Args:
            channel_url: The URL of the YouTube channel. Can be in any valid format:
                        - https://www.youtube.com/channel/UC...
                        - https://www.youtube.com/c/ChannelName
                        - https://www.youtube.com/@handle
            max_results: Maximum number of videos to retrieve (default: 50)
            
        Returns:
            List[str]: List of video IDs from the channel
            
        Raises:
            ValueError: If the channel is not found or URL is invalid
            HttpError: If there is an error with the YouTube API
            
        Example:
            >>> api = YouTubeAPI()
            >>> video_ids = api.get_channel_video_ids("https://www.youtube.com/@example")
            >>> print(len(video_ids))
            50
        """
        channel_id = self.get_channel_id(channel_url)
        videos = self.get_channel_videos(channel_id, max_results)
        return [video['video_id'] for video in videos]

    def get_video_details(self, video_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a YouTube video.
        
        Args:
            video_url: The URL of the YouTube video
            
        Returns:
            Dict containing video details including id, title, description,
            publish date, duration, view count, and like count
            
        Raises:
            ValueError: If the video URL is invalid
            Exception: If there is an error with the YouTube API
        """
        if not self.is_valid_video_url(video_url):
            raise ValueError("Invalid YouTube video URL")
        
        video_id = video_url.split('v=')[1].split('&')[0]
        
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                raise Exception("Video not found")
            
            video = response['items'][0]
            return {
                'id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'published_at': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'view_count': video['statistics'].get('viewCount', '0'),
                'like_count': video['statistics'].get('likeCount', '0')
            }
        except HttpError as e:
            raise Exception("YouTube API error") from e

    def get_video_info(self, video_id: str) -> dict:
        """
        Get information about a specific YouTube video.
        
        Args:
            video_id (str): The ID of the YouTube video
            
        Returns:
            dict: Dictionary containing video information
            
        Raises:
            HttpError: If there's an error retrieving the video information
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"No video found with ID: {video_id}")
                
            video_data = response['items'][0]
            return {
                'id': video_data['id'],
                'title': video_data['snippet']['title'],
                'description': video_data['snippet']['description'],
                'published_at': video_data['snippet']['publishedAt'],
                'duration': video_data['contentDetails']['duration'],
                'view_count': video_data['statistics'].get('viewCount', 0),
                'like_count': video_data['statistics'].get('likeCount', 0),
                'comment_count': video_data['statistics'].get('commentCount', 0)
            }
        except HttpError as e:
            raise HttpError(e.resp, e.content)

    def get_channel_info(self, channel_id: str) -> dict:
        """
        Get information about a specific YouTube channel.
        
        Args:
            channel_id (str): The ID of the YouTube channel
            
        Returns:
            dict: Dictionary containing channel information
            
        Raises:
            HttpError: If there's an error retrieving the channel information
        """
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"No channel found with ID: {channel_id}")
                
            channel_data = response['items'][0]
            return {
                'id': channel_data['id'],
                'title': channel_data['snippet']['title'],
                'description': channel_data['snippet']['description'],
                'published_at': channel_data['snippet']['publishedAt'],
                'subscriber_count': channel_data['statistics'].get('subscriberCount', 0),
                'video_count': channel_data['statistics'].get('videoCount', 0),
                'view_count': channel_data['statistics'].get('viewCount', 0)
            }
        except HttpError as e:
            raise HttpError(e.resp, e.content)

    def search_videos(self, query: str, max_results: int = 25, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos matching a query.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 25)
            **kwargs: Additional search parameters (e.g., order, publishedAfter)
            
        Returns:
            List of dictionaries containing video information
            
        Raises:
            HttpError: If there is an error with the YouTube API
        """
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': min(max_results, 50)  # YouTube API limit
        }
        search_params.update(kwargs)
        
        request = self.youtube.search().list(**search_params)
        response = request.execute()
        
        videos = []
        for item in response.get('items', []):
            videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle']
            })
        
        return videos

    def get_playlist_video_ids(self, playlist_id: str, max_results: Optional[int] = None) -> List[str]:
        """
        Get video IDs from a YouTube playlist.
        
        Args:
            playlist_id: The ID of the playlist
            max_results: Maximum number of videos to retrieve (optional)
            
        Returns:
            List of video IDs from the playlist
            
        Raises:
            ValueError: If no videos are found in the playlist
            HttpError: If there is an error with the YouTube API
        """
        video_ids = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,  # YouTube API maximum
                pageToken=next_page_token
            )
            
            response = request.execute()
            items = response.get('items', [])
            
            if not items and not video_ids:
                raise ValueError("No videos found in playlist")
            
            for item in items:
                video_ids.append(item['contentDetails']['videoId'])
                if max_results and len(video_ids) >= max_results:
                    return video_ids[:max_results]
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
        return video_ids 