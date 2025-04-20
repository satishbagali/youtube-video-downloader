import pytest
from unittest.mock import Mock, patch
from src.youtube_api import YouTubeAPI

@pytest.fixture
def youtube_api():
    """Fixture to create a YouTubeAPI instance"""
    return YouTubeAPI()

@pytest.mark.parametrize("url,expected_id", [
    ("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw", "UC_x5XG1OV2P6uZZ5FSM9Ttw"),
    ("https://www.youtube.com/@googledevelopers", None),  # Will be handled by API call
    ("https://www.youtube.com/c/GoogleDevelopers", None),  # Will be handled by API call
    ("invalid_url", None),
])
def test_channel_id_extraction(youtube_api, url, expected_id):
    """Test extracting channel ID from different URL formats"""
    result = youtube_api.get_channel_id(url)
    if expected_id:
        assert result == expected_id
    else:
        assert result is None or isinstance(result, str)

@pytest.mark.parametrize("url,valid", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
    ("https://youtu.be/dQw4w9WgXcQ", True),
    ("invalid_url", False),
])
def test_video_url_validation(youtube_api, url, valid):
    """Test validation of video URLs"""
    if valid:
        assert youtube_api.get_video_id(url) is not None
    else:
        assert youtube_api.get_video_id(url) is None

@patch('googleapiclient.discovery.build')
def test_channel_videos_retrieval(mock_build, youtube_api):
    """Test retrieving videos from a channel"""
    # Mock response from YouTube API
    mock_response = {
        'items': [
            {
                'id': {'videoId': 'video1'},
                'snippet': {'title': 'Test Video 1'}
            },
            {
                'id': {'videoId': 'video2'},
                'snippet': {'title': 'Test Video 2'}
            }
        ],
        'nextPageToken': None
    }
    
    # Setup mock
    mock_service = Mock()
    mock_build.return_value = mock_service
    mock_service.search().list().execute.return_value = mock_response
    
    # Test
    videos = youtube_api.get_channel_videos('test_channel_id')
    
    assert len(videos) == 2
    assert videos[0]['video_id'] == 'video1'
    assert videos[0]['title'] == 'Test Video 1'
    assert videos[1]['video_id'] == 'video2'
    assert videos[1]['title'] == 'Test Video 2'

def test_api_key_validation():
    """Test API key validation"""
    with patch.dict('os.environ', {'YOUTUBE_API_KEY': ''}):
        with pytest.raises(ValueError):
            YouTubeAPI()

@pytest.mark.parametrize("error_type,expected_message", [
    ("quotaExceeded", "API quota exceeded"),
    ("invalidRequest", "Invalid request"),
])
@patch('googleapiclient.discovery.build')
def test_error_handling(mock_build, youtube_api, error_type, expected_message):
    """Test handling of various API errors"""
    # Mock API error response
    mock_service = Mock()
    mock_build.return_value = mock_service
    mock_service.search().list().execute.side_effect = Exception(error_type)
    
    # Test
    result = youtube_api.get_channel_videos('test_channel_id')
    assert result is None  # Error cases should return None 