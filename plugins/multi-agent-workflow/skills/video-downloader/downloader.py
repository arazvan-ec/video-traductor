"""Multi-strategy video downloader."""

import os
import re
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from abc import ABC, abstractmethod

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class DownloadResult:
    """Result of a download attempt."""
    success: bool
    video_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    error: Optional[str] = None
    strategy_used: Optional[str] = None


class DownloadStrategy(ABC):
    """Base class for download strategies."""

    name: str = "base"

    @abstractmethod
    def download(self, url: str, output_dir: Path, options: dict) -> DownloadResult:
        """Attempt to download video."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this strategy can be used."""
        pass


class YtDlpDirectStrategy(DownloadStrategy):
    """Direct yt-dlp download."""

    name = "yt-dlp-direct"

    def is_available(self) -> bool:
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def download(self, url: str, output_dir: Path, options: dict) -> DownloadResult:
        quality = options.get("quality", "720p")
        format_str = self._get_format_string(quality)

        # Get video info first
        info_cmd = [
            "yt-dlp",
            "--no-check-certificate",
            "--geo-bypass",
            "--dump-json",
            "--no-download",
            url
        ]

        try:
            result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return DownloadResult(
                    success=False,
                    error=f"Failed to get video info: {result.stderr}",
                    strategy_used=self.name
                )

            info = json.loads(result.stdout)
            title = self._sanitize_filename(info.get("title", "video"))
            duration = info.get("duration", 0)

        except subprocess.TimeoutExpired:
            return DownloadResult(
                success=False,
                error="Timeout getting video info",
                strategy_used=self.name
            )
        except json.JSONDecodeError:
            return DownloadResult(
                success=False,
                error="Failed to parse video info",
                strategy_used=self.name
            )

        video_path = output_dir / f"{title}.mp4"
        audio_path = output_dir / f"{title}.wav"

        # Download video
        download_cmd = [
            "yt-dlp",
            "--no-check-certificate",
            "--geo-bypass",
            "-f", format_str,
            "-o", str(video_path),
            "--no-playlist",
            "--retries", "3",
            url
        ]

        try:
            result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                return DownloadResult(
                    success=False,
                    error=f"Download failed: {result.stderr}",
                    strategy_used=self.name
                )
        except subprocess.TimeoutExpired:
            return DownloadResult(
                success=False,
                error="Download timeout",
                strategy_used=self.name
            )

        # Extract audio
        if options.get("extract_audio", True):
            self._extract_audio(video_path, audio_path)

        return DownloadResult(
            success=True,
            video_path=video_path,
            audio_path=audio_path if audio_path.exists() else None,
            title=title,
            duration=duration,
            strategy_used=self.name
        )

    def _get_format_string(self, quality: str) -> str:
        quality_map = {
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "best": "bestvideo+bestaudio/best",
        }
        return quality_map.get(quality, quality_map["720p"])

    def _sanitize_filename(self, filename: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = sanitized.replace(' ', '_')
        return sanitized[:100]

    def _extract_audio(self, video_path: Path, audio_path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(audio_path)
        ]
        subprocess.run(cmd, capture_output=True)


class CobaltStrategy(DownloadStrategy):
    """Download using Cobalt API (cobalt.tools)."""

    name = "cobalt-api"

    def __init__(self):
        self.api_url = os.environ.get("COBALT_API", "https://api.cobalt.tools")

    def is_available(self) -> bool:
        return HAS_REQUESTS

    def download(self, url: str, output_dir: Path, options: dict) -> DownloadResult:
        if not HAS_REQUESTS:
            return DownloadResult(
                success=False,
                error="requests library not available",
                strategy_used=self.name
            )

        try:
            # Call Cobalt API
            response = requests.post(
                f"{self.api_url}/api/json",
                json={
                    "url": url,
                    "vCodec": "h264",
                    "vQuality": options.get("quality", "720"),
                    "aFormat": "wav",
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30
            )

            if response.status_code != 200:
                return DownloadResult(
                    success=False,
                    error=f"Cobalt API error: {response.status_code}",
                    strategy_used=self.name
                )

            data = response.json()

            if data.get("status") == "error":
                return DownloadResult(
                    success=False,
                    error=f"Cobalt error: {data.get('text', 'Unknown error')}",
                    strategy_used=self.name
                )

            # Download the video from the URL provided by Cobalt
            download_url = data.get("url")
            if not download_url:
                return DownloadResult(
                    success=False,
                    error="No download URL in response",
                    strategy_used=self.name
                )

            # Download file
            title = self._extract_video_id(url)
            video_path = output_dir / f"{title}.mp4"

            video_response = requests.get(download_url, stream=True, timeout=300)
            with open(video_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract audio
            audio_path = output_dir / f"{title}.wav"
            if options.get("extract_audio", True):
                self._extract_audio(video_path, audio_path)

            return DownloadResult(
                success=True,
                video_path=video_path,
                audio_path=audio_path if audio_path.exists() else None,
                title=title,
                strategy_used=self.name
            )

        except requests.RequestException as e:
            return DownloadResult(
                success=False,
                error=f"Request error: {str(e)}",
                strategy_used=self.name
            )

    def _extract_video_id(self, url: str) -> str:
        patterns = [
            r'(?:v=|/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return "video"

    def _extract_audio(self, video_path: Path, audio_path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(audio_path)
        ]
        subprocess.run(cmd, capture_output=True)


class InvidiousStrategy(DownloadStrategy):
    """Download using Invidious API."""

    name = "invidious-api"

    # Public Invidious instances
    INSTANCES = [
        "https://invidious.snopyta.org",
        "https://yewtu.be",
        "https://invidious.kavin.rocks",
        "https://vid.puffyan.us",
        "https://invidious.namazso.eu",
    ]

    def __init__(self):
        custom_instance = os.environ.get("INVIDIOUS_INSTANCE")
        if custom_instance:
            self.INSTANCES.insert(0, custom_instance)

    def is_available(self) -> bool:
        return HAS_REQUESTS

    def download(self, url: str, output_dir: Path, options: dict) -> DownloadResult:
        if not HAS_REQUESTS:
            return DownloadResult(
                success=False,
                error="requests library not available",
                strategy_used=self.name
            )

        video_id = self._extract_video_id(url)
        if not video_id:
            return DownloadResult(
                success=False,
                error="Could not extract video ID",
                strategy_used=self.name
            )

        # Try each instance
        for instance in self.INSTANCES:
            result = self._try_instance(instance, video_id, output_dir, options)
            if result.success:
                return result

        return DownloadResult(
            success=False,
            error="All Invidious instances failed",
            strategy_used=self.name
        )

    def _try_instance(self, instance: str, video_id: str, output_dir: Path, options: dict) -> DownloadResult:
        try:
            # Get video info
            info_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(info_url, timeout=15)

            if response.status_code != 200:
                return DownloadResult(success=False, error=f"Instance {instance} returned {response.status_code}")

            data = response.json()
            title = self._sanitize_filename(data.get("title", video_id))
            duration = data.get("lengthSeconds", 0)

            # Find best format
            formats = data.get("formatStreams", []) + data.get("adaptiveFormats", [])
            video_url = None

            for fmt in formats:
                if fmt.get("container") == "mp4" and fmt.get("type", "").startswith("video"):
                    video_url = fmt.get("url")
                    break

            if not video_url:
                # Fallback to any available format
                for fmt in formats:
                    if fmt.get("url"):
                        video_url = fmt.get("url")
                        break

            if not video_url:
                return DownloadResult(success=False, error="No download URL found")

            # Download video
            video_path = output_dir / f"{title}.mp4"
            video_response = requests.get(video_url, stream=True, timeout=300)

            with open(video_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract audio
            audio_path = output_dir / f"{title}.wav"
            if options.get("extract_audio", True):
                self._extract_audio(video_path, audio_path)

            return DownloadResult(
                success=True,
                video_path=video_path,
                audio_path=audio_path if audio_path.exists() else None,
                title=title,
                duration=duration,
                strategy_used=f"{self.name}:{instance}"
            )

        except Exception as e:
            return DownloadResult(success=False, error=str(e))

    def _extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:v=|/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _sanitize_filename(self, filename: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = sanitized.replace(' ', '_')
        return sanitized[:100]

    def _extract_audio(self, video_path: Path, audio_path: Path) -> None:
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(audio_path)
        ]
        subprocess.run(cmd, capture_output=True)


class VideoDownloaderSkill:
    """Multi-strategy video downloader."""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize strategies in order of preference
        self.strategies: List[DownloadStrategy] = [
            YtDlpDirectStrategy(),
            InvidiousStrategy(),
            CobaltStrategy(),
        ]

    def download(
        self,
        url: str,
        quality: str = "720p",
        extract_audio: bool = True,
        strategy: Optional[str] = None
    ) -> DownloadResult:
        """
        Download video using available strategies.

        Args:
            url: Video URL
            quality: Video quality (360p, 480p, 720p, 1080p, best)
            extract_audio: Whether to extract audio to WAV
            strategy: Force specific strategy (yt-dlp-direct, invidious-api, cobalt-api)

        Returns:
            DownloadResult with paths to downloaded files
        """
        options = {
            "quality": quality,
            "extract_audio": extract_audio,
        }

        # If specific strategy requested
        if strategy:
            for s in self.strategies:
                if s.name == strategy:
                    if s.is_available():
                        return s.download(url, self.output_dir, options)
                    else:
                        return DownloadResult(
                            success=False,
                            error=f"Strategy {strategy} is not available",
                            strategy_used=strategy
                        )
            return DownloadResult(
                success=False,
                error=f"Unknown strategy: {strategy}"
            )

        # Try each strategy
        errors = []
        for s in self.strategies:
            if not s.is_available():
                print(f"  Skipping {s.name}: not available")
                continue

            print(f"  Trying {s.name}...")
            result = s.download(url, self.output_dir, options)

            if result.success:
                print(f"  Success with {s.name}!")
                return result

            errors.append(f"{s.name}: {result.error}")
            print(f"  Failed: {result.error}")

        return DownloadResult(
            success=False,
            error=f"All strategies failed: {'; '.join(errors)}"
        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Download videos using multiple strategies")
    parser.add_argument("url", help="Video URL")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("-q", "--quality", default="720p",
                       choices=["360p", "480p", "720p", "1080p", "best"],
                       help="Video quality")
    parser.add_argument("--extract-audio", action="store_true", default=True,
                       help="Extract audio to WAV")
    parser.add_argument("--strategy", help="Force specific strategy")

    args = parser.parse_args()

    skill = VideoDownloaderSkill(output_dir=args.output)
    print(f"Downloading: {args.url}")

    result = skill.download(
        url=args.url,
        quality=args.quality,
        extract_audio=args.extract_audio,
        strategy=args.strategy
    )

    if result.success:
        print(f"\nSuccess!")
        print(f"  Video: {result.video_path}")
        if result.audio_path:
            print(f"  Audio: {result.audio_path}")
        print(f"  Strategy: {result.strategy_used}")
    else:
        print(f"\nFailed: {result.error}")
        exit(1)


if __name__ == "__main__":
    main()
