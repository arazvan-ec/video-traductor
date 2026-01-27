"""YouTube video downloader using yt-dlp."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import re


@dataclass
class VideoInfo:
    """Video metadata."""
    id: str
    title: str
    duration: int  # seconds
    uploader: str
    description: str


@dataclass
class DownloadResult:
    """Result of video download."""
    video_path: Path
    audio_path: Path
    info: VideoInfo


class VideoDownloader:
    """Download videos from YouTube using yt-dlp."""

    def __init__(self, output_dir: Path):
        """Initialize downloader with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_info(self, url: str) -> VideoInfo:
        """Get video metadata without downloading."""
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        return VideoInfo(
            id=data.get("id", ""),
            title=data.get("title", "Unknown"),
            duration=data.get("duration", 0),
            uploader=data.get("uploader", "Unknown"),
            description=data.get("description", "")
        )

    def download(self, url: str) -> DownloadResult:
        """Download video and extract audio."""
        # Get video info first
        info = self.get_info(url)

        # Sanitize filename
        safe_title = self._sanitize_filename(info.title)
        video_path = self.output_dir / f"{safe_title}.mp4"
        audio_path = self.output_dir / f"{safe_title}.wav"

        # Download video
        print(f"Downloading: {info.title}")
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", str(video_path),
            "--no-playlist",
            url
        ]
        subprocess.run(cmd, check=True)

        # Extract audio
        print("Extracting audio...")
        self.extract_audio(video_path, audio_path)

        return DownloadResult(
            video_path=video_path,
            audio_path=audio_path,
            info=info
        )

    def extract_audio(self, video_path: Path, output_path: Path) -> Path:
        """Extract audio from video file."""
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", "16000",  # 16kHz for Whisper
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Limit length
        return sanitized[:100]
