"""
This test suite verifies the functionality of the VideoDownloader class, which handles YouTube video downloads.
It tests the complete download workflow including initialization, video information extraction,
single and batch video downloads, progress tracking, and error handling scenarios.
The tests use mocking to simulate YouTube-DL interactions without actual network calls.
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.video_downloader import VideoDownloader
from config.settings import Config

@pytest.fixture
def video_downloader():
    """
    Fixture to create a VideoDownloader instance with a test directory.
    Creates a temporary download directory for testing and cleans it up after tests are complete.
    The cleanup ensures no test files are left behind.
    """
    test_dir = os.path.join(os.path.dirname(__file__), 'test_downloads')
    downloader = VideoDownloader(output_dir=test_dir)
    yield downloader
    # Cleanup: Remove test directory after tests
    if os.path.exists(test_dir):
        for file in os.listdir(test_dir):
            os.remove(os.path.join(test_dir, file))
        os.rmdir(test_dir)

def test_initialization(video_downloader):
    """
    Test VideoDownloader initialization and configuration.
    Verifies that the output directory is created and all yt-dlp options
    are properly set with correct default values.
    """
    assert os.path.exists(video_downloader.output_dir)
    assert video_downloader.ydl_opts['format'] == 'best[height<=720]'
    assert video_downloader.ydl_opts['noplaylist'] is True
    assert callable(video_downloader.ydl_opts['progress_hooks'][0])

@patch('yt_dlp.YoutubeDL')
def test_successful_video_download(mock_ytdl, video_downloader):
    """
    Test successful video download scenario.
    Mocks the YouTube-DL library to simulate a successful video download,
    verifies that video info is extracted and download is initiated with correct parameters.
    """
    # Mock video info
    mock_info = {
        'title': 'Test Video',
        'duration': 120
    }
    
    # Configure mock
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = mock_info
    mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
    
    # Test download
    result = video_downloader.download_video('https://www.youtube.com/watch?v=test123')
    
    assert result is True
    mock_ytdl_instance.extract_info.assert_called_once_with(
        'https://www.youtube.com/watch?v=test123',
        download=False
    )
    mock_ytdl_instance.download.assert_called_once_with(
        ['https://www.youtube.com/watch?v=test123']
    )

@patch('yt_dlp.YoutubeDL')
def test_failed_video_info_extraction(mock_ytdl, video_downloader):
    """
    Test handling of failed video info extraction.
    Simulates a scenario where video information cannot be retrieved,
    ensuring the downloader handles the failure gracefully and returns False
    without attempting to download.
    """
    # Configure mock to return None for video info
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = None
    mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
    
    # Test download
    result = video_downloader.download_video('https://www.youtube.com/watch?v=invalid')
    
    assert result is False
    mock_ytdl_instance.download.assert_not_called()

@patch('yt_dlp.YoutubeDL')
def test_download_exception_handling(mock_ytdl, video_downloader):
    """
    Test exception handling during video download.
    Verifies that the downloader properly handles and recovers from exceptions
    that might occur during the download process, ensuring robust error handling.
    """
    # Configure mock to raise an exception
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.side_effect = Exception("Download failed")
    mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
    
    # Test download
    result = video_downloader.download_video('https://www.youtube.com/watch?v=error')
    
    assert result is False

def test_multiple_video_download(video_downloader):
    """
    Test batch downloading of multiple videos.
    Verifies that the downloader can handle multiple video URLs,
    tracks success/failure for each download, and returns accurate results
    for the batch operation.
    """
    with patch.object(video_downloader, 'download_video') as mock_download:
        # Mock download results
        mock_download.side_effect = [True, False, True]
        
        # Test multiple downloads
        urls = [
            'https://www.youtube.com/watch?v=video1',
            'https://www.youtube.com/watch?v=video2',
            'https://www.youtube.com/watch?v=video3'
        ]
        results = video_downloader.download_multiple_videos(urls)
        
        assert results == [True, False, True]
        assert mock_download.call_count == 3

def test_progress_hook(video_downloader, capsys):
    """
    Test progress reporting functionality.
    Verifies that the progress hook correctly formats and displays
    download progress information including percentage and speed.
    Also checks that completion message is shown when download finishes.
    """
    # Test downloading status
    d = {
        'status': 'downloading',
        '_percent_str': '50.0%',
        '_speed_str': '1.00 MiB/s'
    }
    video_downloader.progress_hook(d)
    captured = capsys.readouterr()
    assert '50.0%' in captured.out
    assert '1.00 MiB/s' in captured.out
    
    # Test finished status
    d = {'status': 'finished'}
    video_downloader.progress_hook(d)
    captured = capsys.readouterr()
    assert 'Download completed!' in captured.out

def test_progress_hook_error_handling(video_downloader):
    """
    Test error handling in progress reporting.
    Ensures that the progress hook gracefully handles missing or invalid
    progress information without crashing or affecting the download process.
    This is crucial for maintaining download stability.
    """
    # Test with missing fields
    d = {'status': 'downloading'}  # Missing percent and speed
    try:
        video_downloader.progress_hook(d)
    except Exception as e:
        pytest.fail(f"Progress hook should handle missing fields gracefully: {e}") 