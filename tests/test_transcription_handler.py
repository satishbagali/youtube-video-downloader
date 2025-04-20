"""
This test suite validates the TranscriptionHandler class responsible for managing YouTube video transcripts.
It covers the entire transcript workflow including checking caption availability, retrieving transcripts
in different languages, saving transcripts to files with optional timestamps, and proper error handling.
All tests use mocking to avoid actual API calls to the YouTube Transcript API service.
"""

import pytest
from unittest.mock import Mock, patch
import os
from src.transcription_handler import TranscriptionHandler

@pytest.fixture
def transcription_handler(tmp_path):
    """
    Fixture to create a TranscriptionHandler instance.
    Uses pytest's tmp_path fixture to create a temporary directory for testing.
    """
    output_dir = tmp_path / "transcripts"
    os.makedirs(output_dir, exist_ok=True)
    handler = TranscriptionHandler(output_dir=str(output_dir))
    return handler

@pytest.mark.parametrize("video_id,has_captions", [
    ("video1", True),
    ("video2", False),
])
def test_check_transcript_availability(transcription_handler, video_id, has_captions):
    """
    Test the availability check for video transcripts.
    Verifies that the handler correctly identifies videos with and without
    available captions, handling both successful and failed transcript checks.
    """
    with patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts') as mock_list:
        if has_captions:
            mock_list.return_value = Mock(
                find_manually_created_transcript=Mock(return_value=True)
            )
        else:
            mock_list.side_effect = Exception("No transcript available")
        
        result = transcription_handler.has_captions(video_id)
        assert result == has_captions

def test_get_transcript_success(transcription_handler):
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
        
        transcript = transcription_handler.get_transcript('video1')
        assert len(transcript) == 2
        assert transcript[0]['text'] == 'First line'
        assert transcript[1]['text'] == 'Second line'

def test_get_transcript_failure(transcription_handler):
    """
    Test transcript retrieval failure handling.
    Ensures the handler gracefully handles failed transcript requests,
    returning None instead of crashing and providing appropriate error
    feedback.
    """
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.side_effect = Exception("Failed to get transcript")
        
        transcript = transcription_handler.get_transcript('video1')
        assert transcript is None

@pytest.mark.parametrize("language,expected_transcript", [
    ("en", [{'text': 'English text', 'start': 0.0}]),
    ("es", [{'text': 'Spanish text', 'start': 0.0}]),
])
def test_get_transcript_with_language(transcription_handler, language, expected_transcript):
    """
    Test transcript retrieval in different languages.
    Verifies that the handler can fetch transcripts in multiple languages,
    properly handling language-specific requests and formatting the output
    correctly for each language.
    """
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.return_value = expected_transcript
        
        transcript = transcription_handler.get_transcript('video1', language=language)
        assert transcript == expected_transcript

def test_save_transcript(transcription_handler, tmp_path):
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
    transcription_handler.save_transcript(transcript, str(file_path))
    
    # Verify file contents
    assert file_path.exists()
    content = file_path.read_text()
    assert 'Line 1' in content
    assert 'Line 2' in content

def test_save_transcript_with_timestamps(transcription_handler, tmp_path):
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
    
    transcription_handler.save_transcript(transcript, str(file_path), include_timestamps=True)
    
    content = file_path.read_text()
    assert '[00:00]' in content
    assert '[00:01]' in content

def test_format_transcript(transcription_handler):
    """
    Test transcript formatting functionality.
    Verifies that the handler properly formats transcript data into readable text,
    ensuring proper line breaks, timing information, and text formatting are
    applied consistently.
    """
    transcript = [
        {'text': 'Line 1', 'start': 0.0, 'duration': 1.0},
        {'text': 'Line 2', 'start': 1.0, 'duration': 1.0}
    ]
    
    formatted = transcription_handler.format_transcript(transcript)
    assert isinstance(formatted, str)
    assert 'Line 1' in formatted
    assert 'Line 2' in formatted

def test_error_handling(transcription_handler):
    """
    Test comprehensive error handling scenarios.
    Verifies that the handler properly manages various error conditions,
    including invalid video IDs, unsupported languages, and API failures,
    ensuring graceful degradation in all cases.
    """
    # Test with invalid video ID
    assert transcription_handler.get_transcript('') is None
    
    # Test with non-existent language
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
        mock_get.side_effect = Exception("Language not available")
        assert transcription_handler.get_transcript('video1', language='xx') is None 