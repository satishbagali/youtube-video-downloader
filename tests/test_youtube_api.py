"""Tests for the YouTube API functionality"""
import os
import pytest
from unittest.mock import MagicMock, patch, Mock
from googleapiclient.errors import HttpError
from src.youtube_api import YouTubeAPI
from src.config import Config

@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables for pytest."""
    os.environ['PYTEST_CURRENT_TEST'] = 'test_youtube_api.py::test'
    # Store original environment variables
    original_env = {}
    for key in ['BASE_DIR', 'YOUTUBE_API_KEY', 'TEST_MODE']:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    # Set test environment variables
    os.environ['BASE_DIR'] = '/tmp/test'
    os.environ['YOUTUBE_API_KEY'] = 'test_api_key'
    os.environ['TEST_MODE'] = 'true'
    
    yield
    
    # Restore original environment variables
    for key in ['BASE_DIR', 'YOUTUBE_API_KEY', 'TEST_MODE']:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)
    if 'PYTEST_CURRENT_TEST' in os.environ:
        del os.environ['PYTEST_CURRENT_TEST']

@pytest.fixture
def mock_config(monkeypatch):
    """Mock Config class for testing"""
    mock = MagicMock(spec=Config)
    mock.api_key = "test_api_key"
    return mock

@pytest.fixture
def mock_env():
    """Set up test environment variables"""
    os.environ["YOUTUBE_API_KEY"] = "test_api_key"
    os.environ['BASE_DIR'] = '/tmp'
    yield
    if "YOUTUBE_API_KEY" in os.environ:
        del os.environ["YOUTUBE_API_KEY"]
    os.environ.pop('BASE_DIR', None)

@pytest.fixture
def api(mock_config):
    """Create a YouTubeAPI instance for testing"""
    with patch('src.youtube_api.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        # Ensure mock_config has api_key attribute
        mock_config.api_key = "test_api_key"
        api = YouTubeAPI(config=mock_config)
        api.youtube = mock_youtube
        return api

@pytest.fixture
def youtube_api(mock_config):
    """Create a YouTubeAPI instance with mocked YouTube service."""
    with patch('src.youtube_api.build') as mock_build:
        api = YouTubeAPI(config=mock_config)
        yield api

@pytest.fixture
def mock_youtube_api():
    with patch('src.youtube_api.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        api = YouTubeAPI()
        api.youtube = mock_youtube
        yield api

def test_get_video_info(api):
    """Test retrieving video information"""
    mock_response = {
        'items': [{
            'id': 'test_video_id',
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
                'publishedAt': '2024-01-01T00:00:00Z'
            },
            'contentDetails': {
                'duration': 'PT1H2M10S'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '100',
                'commentCount': '50'
            }
        }]
    }
    
    api.youtube.videos().list.return_value.execute.return_value = mock_response
    
    info = api.get_video_info('test_video_id')
    assert info['title'] == 'Test Video'
    assert info['description'] == 'Test Description'
    assert info['view_count'] == '1000'
    assert info['like_count'] == '100'
    assert info['comment_count'] == '50'

def test_get_video_info_failure(api):
    """Test handling of video info retrieval failure"""
    api.youtube.videos().list.return_value.execute.return_value = {'items': []}
    
    with pytest.raises(ValueError, match='No video found with ID'):
        api.get_video_info('invalid_video_id')

def test_get_channel_info(api):
    """Test retrieving channel information"""
    mock_response = {
        'items': [{
            'id': 'test_channel_id',
            'snippet': {
                'title': 'Test Channel',
                'description': 'Test Channel Description',
                'publishedAt': '2024-01-01T00:00:00Z'
            },
            'statistics': {
                'subscriberCount': '1000',
                'videoCount': '50',
                'viewCount': '5000'
            }
        }]
    }
    
    api.youtube.channels().list.return_value.execute.return_value = mock_response
    
    info = api.get_channel_info('test_channel_id')
    assert info['title'] == 'Test Channel'
    assert info['description'] == 'Test Channel Description'
    assert info['subscriber_count'] == '1000'
    assert info['video_count'] == '50'
    assert info['view_count'] == '5000'

def test_get_channel_info_failure(api):
    """Test handling of channel info retrieval failure"""
    api.youtube.channels().list.return_value.execute.return_value = {'items': []}
    
    with pytest.raises(ValueError, match='No channel found with ID'):
        api.get_channel_info('invalid_channel_id')

def test_search_videos(api):
    """Test searching for videos"""
    mock_response = {
        'items': [{
            'id': {'videoId': 'test_video_id'},
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
                'publishedAt': '2024-01-01T00:00:00Z',
                'channelId': 'test_channel_id',
                'channelTitle': 'Test Channel'
            }
        }]
    }
    
    api.youtube.search().list.return_value.execute.return_value = mock_response
    
    results = api.search_videos('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'test_video_id'
    assert results[0]['title'] == 'Test Video'
    assert results[0]['channel_id'] == 'test_channel_id'
    assert results[0]['channel_title'] == 'Test Channel'

def test_search_videos_with_params(api):
    """Test searching for videos with additional parameters"""
    mock_response = {
        'items': [{
            'id': {'videoId': 'test_video_id'},
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
                'publishedAt': '2024-01-01T00:00:00Z',
                'channelId': 'test_channel_id',
                'channelTitle': 'Test Channel'
            }
        }]
    }
    
    api.youtube.search().list.return_value.execute.return_value = mock_response
    
    results = api.search_videos('test query', max_results=5, order='date')
    assert len(results) == 1
    assert results[0]['id'] == 'test_video_id'
    assert results[0]['title'] == 'Test Video'
    
    # Verify search parameters
    api.youtube.search().list.assert_called_with(
        part='snippet',
        q='test query',
        maxResults=5,
        type='video',
        order='date'
    )

def test_error_handling(api):
    """Test error handling during API requests"""
    api.youtube.search().list.return_value.execute.side_effect = HttpError(
        resp=MagicMock(status=400),
        content=b'API Error'
    )
    
    with pytest.raises(HttpError):
        api.search_videos('test query')

def test_init(youtube_api):
    """Test YouTubeAPI initialization."""
    assert isinstance(youtube_api, YouTubeAPI)
    assert hasattr(youtube_api, 'youtube')

def test_get_channel_videos_success(youtube_api):
    """Test successful retrieval of channel videos."""
    mock_response = {
        'items': [{
            'id': {'videoId': 'video1'},
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
                'publishedAt': '2024-01-01T00:00:00Z'
            }
        }],
        'nextPageToken': None
    }
    youtube_api.youtube.search().list().execute.return_value = mock_response
    videos = youtube_api.get_channel_videos("UC1234567890", max_results=1)
    assert len(videos) == 1
    assert videos[0]['video_id'] == 'video1'
    assert videos[0]['title'] == 'Test Video'

def test_get_channel_videos_pagination(youtube_api):
    """Test pagination in video retrieval."""
    mock_responses = [
        {
            'items': [{
                'id': {'videoId': 'video1'},
                'snippet': {
                    'title': 'Test Video 1',
                    'description': 'Test Description 1',
                    'publishedAt': '2024-01-01T00:00:00Z'
                }
            }],
            'nextPageToken': 'token1'
        },
        {
            'items': [{
                'id': {'videoId': 'video2'},
                'snippet': {
                    'title': 'Test Video 2',
                    'description': 'Test Description 2',
                    'publishedAt': '2024-01-01T00:00:00Z'
                }
            }],
            'nextPageToken': None
        }
    ]
    youtube_api.youtube.search().list().execute.side_effect = mock_responses
    videos = youtube_api.get_channel_videos("UC1234567890", max_results=2)
    assert len(videos) == 2
    assert videos[0]['video_id'] == 'video1'
    assert videos[1]['video_id'] == 'video2'

def test_get_channel_videos_error(youtube_api):
    """Test error handling in video retrieval."""
    error = HttpError(
        resp=MagicMock(status=403),
        content=b'Quota exceeded'
    )
    youtube_api.youtube.search().list().execute.side_effect = error
    with pytest.raises(HttpError):
        youtube_api.get_channel_videos("UC1234567890")

def test_get_channel_id_direct_url(youtube_api):
    """Test getting channel ID from a direct URL."""
    channel_id = "UC1234567890"
    assert youtube_api.get_channel_id(f"youtube.com/channel/{channel_id}") == channel_id

def test_get_channel_id_handle_url(youtube_api):
    """Test getting channel ID from a handle URL."""
    mock_response = {
        'items': [{
            'id': {'channelId': 'UC1234567890'},
            'snippet': {'channelId': 'UC1234567890'}
        }]
    }
    youtube_api.youtube.search().list().execute.return_value = mock_response
    assert youtube_api.get_channel_id("youtube.com/@Handle") == 'UC1234567890'

def test_get_channel_id_custom_url(youtube_api):
    """Test getting channel ID from a custom URL."""
    mock_response = {
        'items': [{
            'id': {'channelId': 'UC1234567890'},
            'snippet': {'channelId': 'UC1234567890'}
        }]
    }
    youtube_api.youtube.search().list().execute.return_value = mock_response
    assert youtube_api.get_channel_id("youtube.com/c/CustomName") == 'UC1234567890'

def test_get_channel_id_not_found(youtube_api):
    """Test handling of non-existent channel."""
    youtube_api.youtube.search().list().execute.return_value = {'items': []}
    with pytest.raises(ValueError, match="Channel not found"):
        youtube_api.get_channel_id("youtube.com/c/NonExistentChannel")

@pytest.mark.parametrize("url,expected", [
    ("youtube.com/channel/UC1234567890", "UC1234567890"),
    ("https://www.youtube.com/channel/UC1234567890", "UC1234567890"),
    ("http://youtube.com/channel/UC1234567890", "UC1234567890"),
    ("youtube.com/c/CustomName", None),
    ("youtube.com/user/Username", None),
    ("youtube.com/@Handle", None)
])
def test_extract_channel_id(url, expected):
    """Test channel ID extraction from various URL formats."""
    api = YouTubeAPI()
    assert api.extract_channel_id(url) == expected

@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/watch?v=123456", True),
    ("https://youtu.be/123456", True),
    ("https://youtube.com/playlist?list=123", False),
    ("https://example.com", False)
])
def test_is_valid_video_url(url, expected):
    """Test video URL validation."""
    api = YouTubeAPI()
    assert api.is_valid_video_url(url) == expected

def test_get_video_details(mock_youtube_api):
    # Mock response data
    mock_response = {
        'items': [{
            'id': 'test_video_id',
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
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
    
    # Setup mock
    mock_request = Mock()
    mock_request.execute.return_value = mock_response
    mock_youtube_api.youtube.videos().list.return_value = mock_request
    
    # Test valid video URL
    video_details = mock_youtube_api.get_video_details('https://www.youtube.com/watch?v=test_video_id')
    
    assert video_details['id'] == 'test_video_id'
    assert video_details['title'] == 'Test Video'
    assert video_details['view_count'] == '1000'
    
    # Test invalid video URL
    with pytest.raises(ValueError, match="Invalid YouTube video URL"):
        mock_youtube_api.get_video_details('invalid_url')
    
    # Test API error
    mock_request.execute.side_effect = HttpError(Mock(status=404), b'not found')
    with pytest.raises(Exception, match="YouTube API error"):
        mock_youtube_api.get_video_details('https://www.youtube.com/watch?v=test_video_id')

def test_search_videos(mock_youtube_api):
    # Mock response data
    mock_response = {
        'items': [{
            'id': {'videoId': 'test_video_1'},
            'snippet': {
                'title': 'Test Video 1',
                'description': 'Description 1',
                'publishedAt': '2024-01-01T00:00:00Z',
                'channelId': 'channel_1',
                'channelTitle': 'Test Channel 1'
            }
        }]
    }
    
    # Setup mock
    mock_request = Mock()
    mock_request.execute.return_value = mock_response
    mock_youtube_api.youtube.search().list.return_value = mock_request
    
    # Test search
    results = mock_youtube_api.search_videos('test query', max_results=1)
    
    assert len(results) == 1
    assert results[0]['id'] == 'test_video_1'
    assert results[0]['title'] == 'Test Video 1'
    
    # Test API error
    mock_request.execute.side_effect = HttpError(Mock(status=403), b'quota exceeded')
    with pytest.raises(HttpError):
        mock_youtube_api.search_videos('test query')

def test_get_playlist_video_ids(mock_youtube_api):
    # Mock response data for first page
    mock_response_1 = {
        'items': [
            {'contentDetails': {'videoId': 'video1'}},
            {'contentDetails': {'videoId': 'video2'}}
        ],
        'nextPageToken': 'token123'
    }
    
    # Mock response data for second page
    mock_response_2 = {
        'items': [
            {'contentDetails': {'videoId': 'video3'}}
        ]
    }
    
    # Setup mock for first test case
    mock_request = Mock()
    mock_request.execute.side_effect = [mock_response_1, mock_response_2]
    mock_youtube_api.youtube.playlistItems().list.return_value = mock_request
    
    # Test getting playlist videos
    video_ids = mock_youtube_api.get_playlist_video_ids('playlist123', max_results=3)
    
    assert len(video_ids) == 3
    assert video_ids == ['video1', 'video2', 'video3']
    
    # Setup new mock for empty playlist test
    mock_request_empty = Mock()
    mock_request_empty.execute.return_value = {'items': []}
    mock_youtube_api.youtube.playlistItems().list.return_value = mock_request_empty
    
    # Test empty playlist
    with pytest.raises(ValueError, match="No videos found in playlist"):
        mock_youtube_api.get_playlist_video_ids('empty_playlist')
    
    # Setup new mock for API error test
    mock_request_error = Mock()
    mock_request_error.execute.side_effect = HttpError(Mock(status=404), b'playlist not found')
    mock_youtube_api.youtube.playlistItems().list.return_value = mock_request_error
    
    # Test API error
    with pytest.raises(HttpError):
        mock_youtube_api.get_playlist_video_ids('invalid_playlist') 