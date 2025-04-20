from setuptools import setup, find_packages

setup(
    name="youtube-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2023.12.30",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "browser-cookie3>=0.19.1",
        "fake-useragent>=1.4.0",
        "python-dotenv>=1.0.0",
        "youtube-transcript-api>=0.6.1",
        "google-api-python-client>=2.108.0",
    ],
    python_requires=">=3.8",
) 