import pytest
from unittest.mock import Mock, patch
from src.youtube_api import YouTubeAPI

@pytest.fixture
def mock_credentials():
    """Mock Google credentials"""
    with patch('google.oauth2.credentials.Credentials') as mock_creds:
        mock_creds.return_value = Mock()
        yield mock_creds

@pytest.fixture
def youtube_api(mock_credentials):
    """Create YouTubeAPI instance with mocked credentials"""
    with patch('google.auth.default', return_value=(mock_credentials, 'project')):
        api = YouTubeAPI(api_key='dummy_key')
        return api

def test_api_key_validation(youtube_api):
    """Test API key validation"""
    assert youtube_api.api_key == 'dummy_key'

@pytest.mark.parametrize("url,expected_id", [
    ("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw", "UC_x5XG1OV2P6uZZ5FSM9Ttw"),
    ("https://www.youtube.com/@googledevelopers", None),
    ("https://www.youtube.com/c/GoogleDevelopers", None),
    ("invalid_url", None)
])
def test_channel_id_extraction(youtube_api, url, expected_id):
    """Test channel ID extraction from different URL formats"""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        
        result = youtube_api.extract_channel_id(url)
        assert result == expected_id

@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
    ("https://youtu.be/dQw4w9WgXcQ", True),
    ("invalid_url", False)
])
def test_video_url_validation(youtube_api, url, expected):
    """Test video URL validation"""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        
        result = youtube_api.is_valid_video_url(url)
        assert result == expected

def test_channel_videos_retrieval(youtube_api):
    """Test retrieving videos from a channel"""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_youtube = Mock()
        mock_search = Mock()
        mock_youtube.search.return_value.list.return_value.execute.return_value = {
            'items': [
                {'id': {'videoId': 'video1'}},
                {'id': {'videoId': 'video2'}}
            ]
        }
        mock_build.return_value = mock_youtube
        
        videos = youtube_api.get_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw")
        assert len(videos) == 2
        assert videos[0]['id']['videoId'] == 'video1'

@pytest.mark.parametrize("error_reason,expected_message", [
    ("quotaExceeded", "API quota exceeded"),
    ("invalidRequest", "Invalid request")
])
def test_error_handling(youtube_api, error_reason, expected_message):
    """Test error handling for various API errors"""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_youtube = Mock()
        mock_youtube.search.return_value.list.side_effect = Exception(expected_message)
        mock_build.return_value = mock_youtube
        
        with pytest.raises(Exception) as exc_info:
            youtube_api.get_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw")
        assert str(exc_info.value) == expected_message 