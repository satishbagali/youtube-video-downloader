# YouTube Video Downloader

A Python application that allows you to download videos from YouTube channels and extract their transcriptions. This tool is particularly useful for content creators, researchers, and anyone who needs to archive YouTube content with their associated transcripts. The application provides a user-friendly command-line interface and handles various YouTube URL formats and video qualities.

## Features

- List all videos from a YouTube channel
- Download individual videos or entire channel content
- Extract and save video transcriptions with timestamps
- Support for various video quality options
- Clean and interactive command-line interface

The application is designed to be both powerful and user-friendly. It can handle various YouTube channel formats, download videos in your preferred quality, and automatically extract transcriptions when available. The interactive interface guides you through the process, making it accessible even for users with minimal technical experience.

## Prerequisites

- Python 3.7 or higher
- YouTube Data API v3 key
- FFmpeg (recommended for better video quality)

To get a YouTube Data API key, visit the Google Cloud Console (https://console.cloud.google.com/), create a project, enable the YouTube Data API v3, and generate an API key. This key is essential for accessing YouTube's data and should be kept secure. FFmpeg is recommended for better video quality handling and format conversion capabilities.

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd youtube-video-downloader
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your YouTube API key:
```bash
YOUTUBE_API_KEY=your_api_key_here
```

The installation process is straightforward but requires attention to the API key setup. Make sure your `.env` file is properly configured and never commit it to version control. If you're behind a proxy or have special network requirements, you might need to configure those settings in your environment as well.

## Project Structure

```
├── config/
│   └── settings.py         # Configuration and environment settings
├── src/
│   ├── video_downloader.py # Video download functionality
│   ├── transcription_handler.py # Transcription extraction
│   └── youtube_api.py      # YouTube API interactions
├── downloads/              # Downloaded videos storage
├── transcripts/           # Extracted transcriptions storage
├── requirements.txt       # Project dependencies
├── main.py               # Main application entry point
└── README.md             # Project documentation
```

The project follows a modular structure for better organization and maintainability. The `src` directory contains the core functionality split into logical components, while configuration and settings are kept separate in the `config` directory. Downloaded content is organized in dedicated directories for easy access and management.

## Usage

1. Run the program:
```bash
python main.py
```

2. Enter a YouTube channel URL when prompted. The program accepts various URL formats:
   - Channel URLs: `https://www.youtube.com/channel/[CHANNEL_ID]`
   - Custom URLs: `https://www.youtube.com/c/[CUSTOM_NAME]`
   - Handle URLs: `https://www.youtube.com/@[HANDLE]`

3. Choose from the available options:
   - Enter a video number to download a specific video
   - Type 'all' to download all videos
   - Type 'b' to go back to channel URL input
   - Type 'q' to quit

4. The program will:
   - Download the selected video(s) to the `downloads/` directory
   - Extract transcriptions (if available) to the `transcripts/` directory
   - Show progress and status information

The program provides real-time feedback during the download and transcription process. Progress bars show download status, and you'll receive notifications about successful downloads and any issues that arise. Videos are saved with clean, meaningful filenames, and transcriptions are formatted for easy reading with timestamps.

## Dependencies

The project uses several key dependencies:

- `yt-dlp`: Core library for downloading YouTube videos
- `youtube-transcript-api`: For extracting video transcriptions
- `google-api-python-client`: Official Google API client for YouTube Data API
- `python-dotenv`: Environment variable management
- Additional utilities for enhanced functionality

Each dependency serves a specific purpose in the application. yt-dlp provides robust video downloading capabilities with format selection and progress tracking. The youtube-transcript-api handles caption extraction, while the Google API client manages channel and video metadata retrieval. These libraries are regularly updated to maintain compatibility with YouTube's platform.

## Features in Detail

### Video Download
- Downloads videos in the best available quality (up to 720p)
- Shows download progress and speed
- Creates a clean filename based on the video title

The video downloader component automatically selects the best quality version available within the 720p limit to balance quality and download size. It handles various video formats and codecs, with progress tracking and estimated completion time display. Failed downloads are automatically retried with exponential backoff.

### Transcription Extraction
- Extracts available closed captions/subtitles
- Formats transcriptions with timestamps [MM:SS]
- Saves transcriptions in easily readable text format

The transcription feature attempts to extract closed captions when available. It handles multiple caption formats and languages, converting them into a clean, timestamped text format. Each transcription is saved alongside its video, making it easy to reference and search through the content later.

### Channel Processing
- Fetches complete channel video list
- Supports different types of channel URLs
- Provides options for batch or individual video processing

The channel processing system can handle various YouTube channel URL formats and automatically extracts the channel ID. It retrieves the complete video list, including unlisted videos (if accessible), and allows for selective downloading. The batch processing feature includes resume capability for interrupted downloads.

## Error Handling

The program includes robust error handling for:
- Invalid YouTube URLs
- Missing API keys
- Network issues
- Unavailable videos
- Missing transcriptions
- File system errors

Error handling is designed to be informative and user-friendly. When an error occurs, the program provides clear messages about what went wrong and how to fix it. For network-related issues, the program implements automatic retries with exponential backoff. File system errors are handled gracefully to prevent data loss or corruption.

## Best Practices

1. Keep your API key secure in the `.env` file
2. Install FFmpeg for better video quality options
3. Ensure sufficient disk space for downloads
4. Check video availability and transcription presence

Following these best practices ensures optimal performance and reliability. Regular maintenance of the downloads directory prevents disk space issues. The API key should be rotated periodically for security, and the program should be run with appropriate permissions for file operations.

## Contributing

Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## License

[Your chosen license]

## Acknowledgments

- YouTube Data API v3
- Various open-source libraries used in this project

## Troubleshooting Guide

Here are some common errors you might encounter and their solutions:

### API Related Issues

1. **"API key expired. Please renew the API key"**
   - Your YouTube API key has expired or been revoked
   - Solution: Generate a new API key in Google Cloud Console and update it in `.env` file

2. **"Quota exceeded"**
   - You've hit YouTube API's daily quota limit
   - Solution: Wait 24 hours or use a different API key

### Download Issues

1. **"Video unavailable"**
   - Video might be private, deleted, or region-restricted
   - Solution: Check if video is accessible in your browser first

2. **"FFmpeg not found"**
   - FFmpeg is not installed or not in system PATH
   - Solution: Install FFmpeg using package manager:
     ```bash
     # On macOS
     brew install ffmpeg
     # On Ubuntu/Debian
     sudo apt-get install ffmpeg
     ```

### Transcription Issues

1. **"No transcripts found for video"**
   - Video doesn't have closed captions/subtitles
   - Solution: Only auto-generated or manually added captions can be extracted

2. **"Transcripts are disabled for video"**
   - Channel has disabled caption extraction
   - Solution: No workaround available; this is a channel setting

### File System Issues

1. **"Permission denied"**
   - Program lacks write permissions
   - Solution: Check folder permissions or run with appropriate privileges

2. **"No space left on device"**
   - Insufficient disk space
   - Solution: Free up space or change download directory in settings

### Network Issues

1. **"Connection timeout"**
   - Slow internet or server not responding
   - Solution: Check internet connection or try again later

2. **"SSL Certificate Error"**
   - Network configuration or proxy issues
   - Solution: Check system date/time or network proxy settings

For any other errors, check the error message for details or report the issue in the project repository. 