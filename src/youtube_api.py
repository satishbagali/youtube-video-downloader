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