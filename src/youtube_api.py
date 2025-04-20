"""
Module for handling YouTube API interactions
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from src.config import Config

class YouTubeAPI:
    def __init__(self):
        """Initialize the YouTube API client"""
        config = Config()
        self.youtube = build(
            Config.YOUTUBE_API_SERVICE_NAME,
            Config.YOUTUBE_API_VERSION,
            developerKey=config.get_api_key()
        )

    def get_channel_id(self, channel_url):
        """
        Extract channel ID from various forms of YouTube channel URLs
        Returns: Channel ID or None if not found
        """
        try:
            print(f"\nProcessing URL: {channel_url}")
            
            # Ensure the URL starts with http:// or https://
            if not channel_url.startswith(('http://', 'https://')):
                channel_url = 'https://' + channel_url
                if not channel_url.startswith('https://www.'):
                    channel_url = channel_url.replace('https://', 'https://www.')
            elif not channel_url.startswith(('http://www.', 'https://www.')):
                channel_url = channel_url.replace('https://', 'https://www.')
                channel_url = channel_url.replace('http://', 'http://www.')
                
            print(f"Normalized URL: {channel_url}")

            # Handle different URL formats
            parsed_url = urlparse(channel_url)
            
            # Handle youtube.com/channel/[CHANNEL_ID] format
            if '/channel/' in channel_url:
                channel_id = channel_url.split('/channel/')[1].split('/')[0]
                print(f"Found channel ID from /channel/ URL: {channel_id}")
                return channel_id
            
            # Handle youtube.com/c/[CUSTOM_NAME] or youtube.com/user/[USERNAME] or youtube.com/@[HANDLE] format
            elif '/c/' in channel_url or '/user/' in channel_url or '/@' in channel_url:
                # Get username/handle from URL
                if '/@' in channel_url:
                    username = channel_url.split('/@')[1].split('/')[0]
                    print(f"Extracted handle: @{username}")
                else:
                    username = channel_url.split('/')[-1]
                    print(f"Extracted username: {username}")

                # First try with channel handle (new method)
                try:
                    request = self.youtube.search().list(
                        part="snippet",
                        q=f"@{username}",
                        type="channel",
                        maxResults=1
                    )
                    response = request.execute()
                    if response.get('items'):
                        channel_id = response['items'][0]['snippet']['channelId']
                        print(f"Found channel ID using handle search: {channel_id}")
                        return channel_id
                except Exception as e:
                    print(f"Handle search failed: {str(e)}")

                # Then try with forUsername (legacy method)
                try:
                    request = self.youtube.channels().list(
                        part="id",
                        forUsername=username
                    )
                    response = request.execute()
                    if response.get('items'):
                        channel_id = response['items'][0]['id']
                        print(f"Found channel ID using forUsername: {channel_id}")
                        return channel_id
                except Exception as e:
                    print(f"forUsername search failed: {str(e)}")

                # Finally try with general search
                try:
                    request = self.youtube.search().list(
                        part="snippet",
                        q=username,
                        type="channel",
                        maxResults=1
                    )
                    response = request.execute()
                    if response.get('items'):
                        channel_id = response['items'][0]['snippet']['channelId']
                        print(f"Found channel ID using general search: {channel_id}")
                        return channel_id
                except Exception as e:
                    print(f"General search failed: {str(e)}")
            
            print("Could not find channel ID using any method")
            return None

        except Exception as e:
            print(f"Error extracting channel ID: {str(e)}")
            return None

    def extract_channel_id(self, channel_url: str) -> str:
        """
        Extract channel ID from a YouTube channel URL.
        Returns None if the URL format requires an API call to resolve.
        """
        if 'youtube.com/channel/' in channel_url:
            return channel_url.split('youtube.com/channel/')[1].split('/')[0]
        # Custom URLs (/c/) and handle URLs (/@) require API calls
        return None

    def is_valid_video_url(self, url: str) -> bool:
        """
        Check if the given URL is a valid YouTube video URL.
        """
        return ('youtube.com/watch?v=' in url or 'youtu.be/' in url)

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> list:
        """
        Get videos from a YouTube channel.
        
        Args:
            channel_id (str): The ID of the YouTube channel
            max_results (int): Maximum number of videos to retrieve (default: 50)
        
        Returns:
            list: List of dictionaries containing video information
        
        Raises:
            Exception: If there's an error retrieving the videos
        """
        try:
            videos = []
            request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=min(50, max_results),  # API limit is 50 per request
                order="date",
                type="video"
            )
            
            while request and len(videos) < max_results:
                response = request.execute()
                
                for item in response.get('items', []):
                    if len(videos) >= max_results:
                        break
                        
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt']
                    }
                    videos.append(video_info)
                
                # Get the next page if available and needed
                if 'nextPageToken' in response and len(videos) < max_results:
                    request = self.youtube.search().list(
                        part="snippet",
                        channelId=channel_id,
                        maxResults=min(50, max_results - len(videos)),
                        order="date",
                        type="video",
                        pageToken=response['nextPageToken']
                    )
                else:
                    request = None
                    
            return videos
            
        except Exception as e:
            raise Exception(f"Failed to retrieve videos: {str(e)}")

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

    def get_video_details(self, video_url: str) -> dict:
        """
        Get details of a specific video.
        
        Args:
            video_url (str): The URL of the video
            
        Returns:
            dict: Dictionary containing video details
            
        Raises:
            ValueError: If the video URL is invalid
            Exception: If there's an error retrieving video details
        """
        try:
            # Extract video ID from URL
            if not self.is_valid_video_url(video_url):
                raise ValueError("Invalid YouTube video URL")
            
            video_id = video_url.split('v=')[1].split('&')[0] if 'v=' in video_url else video_url.split('/')[-1]
            
            # Get video details from API
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"No video found with ID: {video_id}")
            
            video_info = response['items'][0]
            return {
                'id': video_id,
                'title': video_info['snippet']['title'],
                'description': video_info['snippet']['description'],
                'duration': video_info['contentDetails']['duration'],
                'view_count': video_info['statistics']['viewCount'],
                'like_count': video_info['statistics'].get('likeCount', 0),
                'published_at': video_info['snippet']['publishedAt']
            }
            
        except HttpError as e:
            raise Exception(f"YouTube API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting video details: {str(e)}")

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

    def search_videos(self, query: str, max_results: int = 25, **kwargs) -> list:
        """
        Search for YouTube videos based on a query.
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return (default: 25)
            **kwargs: Additional search parameters (e.g., order, publishedAfter)
            
        Returns:
            list: List of dictionaries containing video information
            
        Raises:
            HttpError: If there's an error performing the search
        """
        try:
            search_params = {
                'part': 'snippet',
                'q': query,
                'maxResults': min(max_results, 50),  # API limit is 50
                'type': 'video',
                **kwargs
            }
            
            request = self.youtube.search().list(**search_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_info = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle']
                }
                videos.append(video_info)
                
            return videos
        except HttpError as e:
            raise HttpError(e.resp, e.content) 