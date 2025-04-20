"""Tests for the YouTube API functionality"""
import os
import pytest
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from src.youtube_api import YouTubeAPI
from src.config import Config

@pytest.fixture
def mock_config(monkeypatch):
    """Mock Config class for testing"""
    mock = MagicMock(spec=Config)
    mock.get_api_key.return_value = "test_api_key"
    
    # Create a mock class with class attributes
    mock_class = MagicMock()
    mock_class.YOUTUBE_API_SERVICE_NAME = "youtube"
    mock_class.YOUTUBE_API_VERSION = "v3"
    mock_class.return_value = mock
    
    monkeypatch.setattr("src.youtube_api.Config", mock_class)
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
def api(mock_config, mock_env):
    """Create a YouTubeAPI instance for testing"""
    with patch('src.youtube_api.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        api = YouTubeAPI()
        api.youtube = mock_youtube
        return api

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