"""
Module for handling YouTube API interactions
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from config.settings import Config

class YouTubeAPI:
    def __init__(self):
        """Initialize the YouTube API client"""
        self.youtube = build(
            Config.YOUTUBE_API_SERVICE_NAME,
            Config.YOUTUBE_API_VERSION,
            developerKey=Config.YOUTUBE_API_KEY
        )

    def get_channel_id(self, channel_url):
        """
        Extract channel ID from various forms of YouTube channel URLs
        Returns: Channel ID or None if not found
        """
        try:
            # Ensure the URL starts with http:// or https://
            if not channel_url.startswith(('http://', 'https://')):
                channel_url = 'https://' + channel_url

            # Handle different URL formats
            parsed_url = urlparse(channel_url)
            
            # Handle youtube.com/channel/[CHANNEL_ID] format
            if '/channel/' in channel_url:
                return channel_url.split('/channel/')[1].split('/')[0]
            
            # Handle youtube.com/c/[CUSTOM_NAME] or youtube.com/user/[USERNAME] format
            elif '/c/' in channel_url or '/user/' in channel_url or '/@' in channel_url:
                # Get username from URL
                if '/@' in channel_url:
                    username = channel_url.split('/@')[1].split('/')[0]
                else:
                    username = channel_url.split('/')[-1]

                # First try with forUsername
                try:
                    request = self.youtube.channels().list(
                        part="id",
                        forUsername=username
                    )
                    response = request.execute()
                    if response['items']:
                        return response['items'][0]['id']
                except:
                    pass

                # If forUsername fails, try with handle
                try:
                    request = self.youtube.search().list(
                        part="snippet",
                        q=username,
                        type="channel",
                        maxResults=1
                    )
                    response = request.execute()
                    if response['items']:
                        return response['items'][0]['snippet']['channelId']
                except:
                    pass
            
            return None

        except Exception as e:
            print(f"Error extracting channel ID: {str(e)}")
            return None

    def get_channel_videos(self, channel_id):
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