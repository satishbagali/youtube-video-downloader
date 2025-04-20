from setuptools import setup, find_packages

setup(
    name="youtube-video-downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "yt-dlp",
        "python-dotenv",
    ],
    python_requires=">=3.11",
) 