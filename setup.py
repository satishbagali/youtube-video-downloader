from setuptools import setup, find_packages

setup(
    name="youtube-video-downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client>=2.108.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=1.0.0",
        "yt-dlp>=2023.12.30",
        "python-dotenv>=1.0.0",
        "youtube-transcript-api>=0.6.1",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
    ],
    python_requires=">=3.11",
) 