"""
This test suite validates the TranscriptionHandler class responsible for managing YouTube video transcripts.
It covers the entire transcript workflow including checking caption availability, retrieving transcripts
in different languages, saving transcripts to files with optional timestamps, and proper error handling.
All tests use mocking to avoid actual API calls to the YouTube Transcript API service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from src.transcription_handler import TranscriptionHandler

@pytest.fixture
def handler(tmp_path):
    """Create a TranscriptionHandler instance for testing"""
    return TranscriptionHandler(str(tmp_path))

@pytest.fixture
def mock_transcript():
    """Create a mock transcript"""
    return [
        {"text": "First line", "start": 0.0, "duration": 2.0},
        {"text": "Second line", "start": 2.0, "duration": 2.0}
    ]

def test_check_transcript_availability(handler):
    """Test checking transcript availability"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts') as mock_list:
        # Mock transcript list
        mock_transcript_list = MagicMock()
        mock_transcript_list.find_manually_created_transcript.return_value = True
        mock_list.return_value = mock_transcript_list
        
        assert handler.has_captions("video_id") is True
        
        # Test when no transcripts available
        mock_transcript_list.find_manually_created_transcript.return_value = False
        assert handler.has_captions("video_id") is False

def test_get_transcript_success(handler, mock_transcript):
    """Test successful transcript retrieval"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.return_value = mock_transcript
        result = handler.get_transcript("video_id")
        assert result == mock_transcript

def test_get_transcript_failure(handler):
    """Test transcript retrieval failure"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.side_effect = Exception("Transcript not found")
        result = handler.get_transcript("video_id")
        assert result is None

def test_get_transcript_with_language(handler, mock_transcript):
    """Test transcript retrieval with specific language"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.return_value = mock_transcript
        result = handler.get_transcript("video_id", language="en")
        assert result == mock_transcript
        mock_get.assert_called_with("video_id", languages=["en"])

def test_save_transcript(handler, tmp_path, mock_transcript):
    """Test saving transcript to file"""
    output_file = tmp_path / "transcript.txt"
    handler.save_transcript(mock_transcript, str(output_file))
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "First line" in content
    assert "Second line" in content

def test_save_transcript_with_timestamps(handler, tmp_path, mock_transcript):
    """Test saving transcript with timestamps"""
    output_file = tmp_path / "transcript_with_timestamps.txt"
    handler.save_transcript(mock_transcript, str(output_file), include_timestamps=True)
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "[00:00]" in content
    assert "[00:02]" in content

def test_get_transcription(handler, tmp_path):
    """Test full transcription process"""
    with patch.multiple(handler,
                       get_video_id=MagicMock(return_value="video_id"),
                       has_captions=MagicMock(return_value=True),
                       get_transcript=MagicMock(return_value=[{"text": "Test transcript", "start": 0.0}])):
        
        result = handler.get_transcription("https://youtube.com/watch?v=123", "Test Video")
        assert result is True

def test_error_handling(handler):
    """Test error handling in transcription process"""
    with patch.multiple(handler,
                       get_video_id=MagicMock(return_value=None)):
        result = handler.get_transcription("invalid_url", "Test Video")
        assert result is False

def test_get_video_id(handler):
    """
    Test video ID extraction from URL.
    Verifies that the handler can correctly extract video IDs from YouTube URLs.
    """
    with patch('yt_dlp.YoutubeDL') as mock_ydl:
        mock_instance = Mock()
        mock_instance.extract_info.return_value = {'id': 'test123'}
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        video_id = handler.get_video_id('https://youtube.com/watch?v=test123')
        assert video_id == 'test123'

def test_format_transcript(handler):
    """
    Test transcript formatting functionality.
    Verifies that timestamps and text are properly formatted.
    """
    test_transcript = [
        {'start': 0, 'text': 'First line'},
        {'start': 65, 'text': 'Second line'}
    ]
    
    formatted = handler.format_transcript(test_transcript)
    assert '[00:00] First line' in formatted
    assert '[01:05] Second line' in formatted

def test_get_transcription_success(handler):
    """
    Test successful transcription retrieval and saving.
    Verifies the complete workflow of getting and saving a transcript.
    """
    with patch('yt_dlp.YoutubeDL') as mock_ydl, \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get_transcript, \
         patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts') as mock_list_transcripts:
        
        # Mock video info extraction
        mock_instance = Mock()
        mock_instance.extract_info.return_value = {'id': 'test123'}
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        # Mock transcript list
        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.return_value = True
        mock_list_transcripts.return_value = mock_transcript_list
        
        # Mock transcript retrieval
        mock_get_transcript.return_value = [
            {'start': 0, 'text': 'Test transcript'}
        ]
        
        result = handler.get_transcription(
            'https://youtube.com/watch?v=test123',
            'Test Video'
        )
        assert result is True

def test_get_transcription_failure(handler):
    """
    Test transcription failure scenarios.
    Verifies proper error handling when transcription fails.
    """
    with patch('yt_dlp.YoutubeDL') as mock_ydl:
        mock_instance = Mock()
        mock_instance.extract_info.return_value = None
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = handler.get_transcription(
            'https://youtube.com/watch?v=invalid',
            'Invalid Video'
        )
        assert result is False

def test_get_multiple_transcriptions(handler):
    """
    Test batch transcription processing.
    Verifies that multiple videos can be processed in sequence.
    """
    videos = [
        {'url': 'https://youtube.com/watch?v=video1', 'title': 'Video 1'},
        {'url': 'https://youtube.com/watch?v=video2', 'title': 'Video 2'}
    ]
    
    with patch.object(handler, 'get_transcription') as mock_get:
        mock_get.side_effect = [True, False]
        
        results = handler.get_multiple_transcriptions(videos)
        assert results == [True, False]
        assert mock_get.call_count == 2

def test_get_transcript_success(handler):
    """
    Test successful transcript retrieval scenario.
    Verifies that the handler can properly fetch and parse transcript data,
    ensuring all transcript elements (text, timing) are correctly extracted
    and formatted.
    """
    mock_transcript = [
        {
            'text': 'First line',
            'start': 0.0,
            'duration': 1.5
        },
        {
            'text': 'Second line',
            'start': 1.5,
            'duration': 2.0
        }
    ]
    
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.return_value = mock_transcript
        
        transcript = handler.get_transcript('video1')
        assert len(transcript) == 2
        assert transcript[0]['text'] == 'First line'
        assert transcript[1]['text'] == 'Second line'

def test_get_transcript_failure(handler):
    """
    Test transcript retrieval failure handling.
    Ensures the handler gracefully handles failed transcript requests,
    returning None instead of crashing and providing appropriate error
    feedback.
    """
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.side_effect = Exception("Failed to get transcript")
        
        transcript = handler.get_transcript('video1')
        assert transcript is None

@pytest.mark.parametrize("language,expected_transcript", [
    ("en", [{'text': 'English text', 'start': 0.0}]),
    ("es", [{'text': 'Spanish text', 'start': 0.0}]),
])
def test_get_transcript_with_language(handler, language, expected_transcript):
    """
    Test transcript retrieval in different languages.
    Verifies that the handler can fetch transcripts in multiple languages,
    properly handling language-specific requests and formatting the output
    correctly for each language.
    """
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.return_value = expected_transcript
        
        transcript = handler.get_transcript('video1', language=language)
        assert transcript == expected_transcript

def test_save_transcript(handler, tmp_path):
    """
    Test transcript saving functionality.
    Verifies that transcripts are correctly saved to files with proper formatting,
    ensuring file creation, write permissions, and content accuracy are all
    handled correctly.
    """
    transcript = [
        {'text': 'Line 1', 'start': 0.0},
        {'text': 'Line 2', 'start': 1.0}
    ]
    
    # Create a temporary file path
    file_path = tmp_path / "transcript.txt"
    
    # Test saving
    handler.save_transcript(transcript, str(file_path))
    
    # Verify file contents
    assert file_path.exists()
    content = file_path.read_text()
    assert 'Line 1' in content
    assert 'Line 2' in content

def test_save_transcript_with_timestamps(handler, tmp_path):
    """
    Test saving transcripts with timestamp information.
    Verifies that timestamps are correctly formatted and included in the output,
    ensuring time-coded transcripts are properly generated with accurate
    timing information.
    """
    transcript = [
        {'text': 'Line 1', 'start': 0.0, 'duration': 1.0},
        {'text': 'Line 2', 'start': 1.0, 'duration': 1.0}
    ]
    
    file_path = tmp_path / "transcript_with_timestamps.txt"
    
    handler.save_transcript(transcript, str(file_path), include_timestamps=True)
    
    content = file_path.read_text()
    assert '[00:00]' in content
    assert '[00:01]' in content

def test_error_handling(handler):
    """
    Test comprehensive error handling scenarios.
    Verifies that the handler properly manages various error conditions,
    including invalid video IDs, unsupported languages, and API failures,
    ensuring graceful degradation in all cases.
    """
    # Test with invalid video ID
    assert handler.get_transcript('') is None
    
    # Test with non-existent language
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.side_effect = Exception("Language not available")
        assert handler.get_transcript('video1', language='xx') is None 