"""Setup script for video-traductor."""

from setuptools import setup, find_packages

setup(
    name="video-traductor",
    version="0.1.0",
    description="Translate YouTube videos to different languages",
    author="Video Traductor Team",
    python_requires=">=3.11",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "yt-dlp>=2024.1.0",
        "openai-whisper>=20231117",
        "ffmpeg-python>=0.2.0",
        "deep-translator>=1.11.4",
        "pysrt>=1.1.2",
        "edge-tts>=6.1.9",
    ],
    entry_points={
        "console_scripts": [
            "video-traductor=video_traductor.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
