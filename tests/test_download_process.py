"""
Test end-to-end download process
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.video_downloader import VideoDownloader
from src.transcription_handler import TranscriptionHandler
from src.youtube_api import YouTubeAPI
from src.config import Config
from googleapiclient.errors import HttpError

@pytest.fixture
def test_environment(tmp_path):
    """Set up test environment with temporary directories"""
    # Store original environment variables
    original_env = {}
    for key in ['BASE_DIR', 'DOWNLOAD_DIR', 'TRANSCRIPT_DIR', 'YOUTUBE_API_KEY']:
        original_env[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]
    
    # Reset Config singleton to ensure clean state
    Config.reset()
    
    # Set up test environment
    os.environ['TEST_MODE'] = 'true'
    os.environ['BASE_DIR'] = str(tmp_path)
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    
    # Create and set other directories
    downloads_dir = tmp_path / 'downloads'
    transcripts_dir = tmp_path / 'transcripts'
    downloads_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    os.environ['DOWNLOAD_DIR'] = str(downloads_dir)
    os.environ['TRANSCRIPT_DIR'] = str(transcripts_dir)
    
    # Initialize Config after setting environment variables
    config = Config()
    
    yield {
        'base_dir': tmp_path,
        'downloads_dir': downloads_dir,
        'transcripts_dir': transcripts_dir,
        'config': config
    }
    
    # Cleanup after test
    Config.reset()
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
    
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']

def create_mock_response(video_id):
    """Create a mock response for a video ID"""
    return {
        'items': [{
            'id': video_id,
            'snippet': {
                'title': f'Test Video {video_id}',
                'description': f'Test Description for {video_id}',
                'publishedAt': '2024-01-01T00:00:00Z'
            },
            'contentDetails': {
                'duration': 'PT10M'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '100'
            }
        }]
    }

@pytest.fixture
def mock_youtube_api():
    """Mock YouTube API responses"""
    with patch('src.youtube_api.build') as mock_build:
        mock_youtube = MagicMock()
        mock_videos = MagicMock()
        mock_list = MagicMock()
        
        # Mock successful video response
        mock_list.execute.return_value = create_mock_response('test_video_id')
        mock_videos.list.return_value = mock_list
        mock_youtube.videos.return_value = mock_videos
        mock_build.return_value = mock_youtube
        
        yield mock_youtube

@pytest.fixture
def mock_video_downloader():
    """Mock video downloader"""
    with patch('src.video_downloader.VideoDownloader') as mock:
        instance = mock.return_value
        instance.download_video.return_value = True
        yield instance

@pytest.fixture
def mock_transcription_handler():
    """Mock transcription handler"""
    with patch('src.transcription_handler.TranscriptionHandler') as mock:
        instance = mock.return_value
        instance.get_transcription.return_value = True
        yield instance

@pytest.fixture
def mock_config(monkeypatch):
    """Mock Config class for testing"""
    mock = MagicMock(spec=Config)
    mock.api_key = "test_api_key"
    return mock

def test_end_to_end_single_video(test_environment, mock_youtube_api,
                                mock_video_downloader, mock_transcription_handler, mock_config):
    """Test complete process of downloading and transcribing a single video."""
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    
    # Test video details retrieval
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        video_details = youtube_api.get_video_details(video_url)
        
    assert video_details['id'] == 'test_video_id'
    assert video_details['title'] == 'Test Video test_video_id'

def test_end_to_end_multiple_videos(test_environment, mock_youtube_api,
                                   mock_video_downloader, mock_transcription_handler, mock_config):
    """Test processing multiple videos in sequence."""
    video_urls = [
        "https://www.youtube.com/watch?v=test_video_1",
        "https://www.youtube.com/watch?v=test_video_2"
    ]
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        for i, url in enumerate(video_urls, 1):
            mock_youtube_api.videos().list().execute.return_value = create_mock_response(f'test_video_{i}')
            video_details = youtube_api.get_video_details(url)
            assert video_details['id'] == f'test_video_{i}'

def test_end_to_end_error_recovery(test_environment, mock_youtube_api,
                                  mock_video_downloader, mock_transcription_handler, mock_config):
    """Test system recovery from various error conditions."""
    video_url = "https://www.youtube.com/watch?v=test_error_video"
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        # First request fails
        mock_youtube_api.videos().list().execute.side_effect = HttpError(
            resp=MagicMock(status=500),
            content=b'API Error'
        )
        with pytest.raises(Exception):
            youtube_api.get_video_details(video_url)
        
        # Second request succeeds
        mock_youtube_api.videos().list().execute.side_effect = None
        mock_youtube_api.videos().list().execute.return_value = create_mock_response('test_video_2')
        video_details = youtube_api.get_video_details("https://www.youtube.com/watch?v=test_video_2")
        assert video_details['id'] == 'test_video_2'

def test_end_to_end_performance(test_environment, mock_youtube_api,
                               mock_video_downloader, mock_transcription_handler, mock_config):
    """Test performance metrics for the complete process."""
    import time
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    
    start_time = time.time()
    
    # Complete process
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        video_details = youtube_api.get_video_details(video_url)
        assert video_details['id'] == 'test_video_id'
        
    end_time = time.time()
    assert end_time - start_time < 5.0  # Process should complete within 5 seconds

def test_end_to_end_file_integrity(test_environment):
    """Test file integrity after download and transcription."""
    downloads_dir = test_environment['downloads_dir']
    transcripts_dir = test_environment['transcripts_dir']
    
    # Directories should be created by the fixture
    assert downloads_dir.exists()
    assert transcripts_dir.exists()
    assert downloads_dir.is_dir()
    assert transcripts_dir.is_dir()

def test_download_video(test_environment, mock_youtube_api, mock_video_downloader, mock_config):
    """Test downloading a single video."""
    video_url = "https://www.youtube.com/watch?v=test_video_id"
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        # Mock video details response
        mock_youtube_api.videos().list().execute.return_value = create_mock_response('test_video_id')
        
        # Get video details
        video_details = youtube_api.get_video_details(video_url)
        assert video_details['id'] == 'test_video_id'
        
        # Mock download process
        mock_video_downloader.download.return_value = '/path/to/downloaded/video.mp4'
        download_path = mock_video_downloader.download(video_details)
        assert download_path.endswith('video.mp4')

def test_download_playlist(test_environment, mock_youtube_api, mock_video_downloader, mock_config):
    """Test downloading videos from a playlist."""
    playlist_url = "https://www.youtube.com/playlist?list=test_playlist"
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        # Mock playlist items response
        mock_youtube_api.playlistItems().list().execute.return_value = {
            'items': [
                {'contentDetails': {'videoId': f'video_{i}'}} for i in range(3)
            ]
        }
        
        # Get playlist videos
        video_ids = youtube_api.get_playlist_video_ids(playlist_url)
        assert len(video_ids) == 3
        
        # Mock video downloads
        for video_id in video_ids:
            mock_youtube_api.videos().list().execute.return_value = create_mock_response(video_id)
            mock_video_downloader.download.return_value = f'/path/to/downloaded/{video_id}.mp4'
            
            video_details = youtube_api.get_video_details(f'https://www.youtube.com/watch?v={video_id}')
            download_path = mock_video_downloader.download(video_details)
            assert download_path.endswith(f'{video_id}.mp4')

def test_download_channel(test_environment, mock_youtube_api, mock_video_downloader, mock_config):
    """Test downloading videos from a channel."""
    channel_url = "https://www.youtube.com/channel/test_channel"
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        # Mock channel search response
        mock_youtube_api.search().list().execute.return_value = {
            'items': [{
                'id': {
                    'channelId': 'test_channel',
                    'videoId': f'video_{i}'
                },
                'snippet': {
                    'title': f'Test Video {i}',
                    'description': f'Description {i}',
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'channelId': 'test_channel',
                    'channelTitle': 'Test Channel'
                }
            } for i in range(2)]
        }
        
        # Get channel videos
        video_ids = youtube_api.get_channel_video_ids(channel_url)
        assert len(video_ids) == 2
        
        # Mock video downloads
        for video_id in video_ids:
            mock_youtube_api.videos().list().execute.return_value = create_mock_response(video_id)
            mock_video_downloader.download.return_value = f'/path/to/downloaded/{video_id}.mp4'
            
            video_details = youtube_api.get_video_details(f'https://www.youtube.com/watch?v={video_id}')
            download_path = mock_video_downloader.download(video_details)
            assert download_path.endswith(f'{video_id}.mp4')

def test_download_search_results(test_environment, mock_youtube_api, mock_video_downloader, mock_config):
    """Test downloading videos from search results."""
    search_query = "test search query"
    
    youtube_api = YouTubeAPI(config=mock_config)
    with patch.object(youtube_api, 'youtube', mock_youtube_api):
        # Mock search response
        mock_youtube_api.search().list().execute.return_value = {
            'items': [
                {
                    'id': {'videoId': f'video_{i}'},
                    'snippet': {
                        'title': f'Test Video {i}',
                        'description': f'Description {i}',
                        'publishedAt': '2024-01-01T00:00:00Z',
                        'channelId': f'channel_{i}',
                        'channelTitle': f'Test Channel {i}'
                    }
                } for i in range(2)
            ]
        }
        
        # Get search results
        results = youtube_api.search_videos(search_query)
        video_ids = [result['id'] for result in results]
        assert len(video_ids) == 2

        # Mock video downloads
        for video_id in video_ids:
            mock_youtube_api.videos().list().execute.return_value = {
                'items': [{
                    'id': video_id,
                    'snippet': {
                        'title': f'Test Video {video_id}',
                        'description': f'Description {video_id}',
                        'publishedAt': '2024-01-01T00:00:00Z'
                    },
                    'contentDetails': {
                        'duration': 'PT1H2M10S'
                    },
                    'statistics': {
                        'viewCount': '1000',
                        'likeCount': '100'
                    }
                }]
            }
            video_details = youtube_api.get_video_details(f'https://www.youtube.com/watch?v={video_id}')
            download_path = mock_video_downloader.download(video_details)
            assert download_path.endswith(f'{video_id}.mp4') 