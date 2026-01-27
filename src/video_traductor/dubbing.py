"""Video dubbing using edge-tts for text-to-speech."""

import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional

from video_traductor.transcriber import Segment


# Voice mapping for different languages
VOICE_MAP = {
    "es": "es-ES-AlvaroNeural",
    "es-MX": "es-MX-DaliaNeural",
    "en": "en-US-GuyNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "pt": "pt-BR-AntonioNeural",
    "it": "it-IT-DiegoNeural",
    "ja": "ja-JP-KeitaNeural",
    "zh-CN": "zh-CN-YunxiNeural",
    "ko": "ko-KR-InJoonNeural",
}


class VideoDubber:
    """Generate dubbed audio and mix with original video."""

    def __init__(self, language: str = "es", voice: Optional[str] = None):
        """
        Initialize dubber.

        Args:
            language: Target language code
            voice: Specific voice to use, or None for default
        """
        self.language = language
        self.voice = voice or VOICE_MAP.get(language, "es-ES-AlvaroNeural")

    async def synthesize_speech_async(
        self,
        segments: List[Segment],
        output_dir: Path
    ) -> List[Path]:
        """
        Synthesize speech for each segment asynchronously.

        Args:
            segments: List of Segment objects with text
            output_dir: Directory to save audio files

        Returns:
            List of paths to generated audio files
        """
        import edge_tts

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_files = []

        print(f"Generating speech for {len(segments)} segments...")

        for i, segment in enumerate(segments):
            output_path = output_dir / f"segment_{i:04d}.mp3"

            communicate = edge_tts.Communicate(segment.text, self.voice)
            await communicate.save(str(output_path))

            audio_files.append(output_path)

            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{len(segments)} audio segments")

        return audio_files

    def synthesize_speech(
        self,
        segments: List[Segment],
        output_dir: Path
    ) -> List[Path]:
        """
        Synchronous wrapper for speech synthesis.

        Args:
            segments: List of Segment objects
            output_dir: Directory for output

        Returns:
            List of audio file paths
        """
        return asyncio.run(self.synthesize_speech_async(segments, output_dir))

    def create_dubbed_audio(
        self,
        segments: List[Segment],
        audio_files: List[Path],
        total_duration: float,
        output_path: Path
    ) -> Path:
        """
        Create single audio track with segments at correct timestamps.

        Args:
            segments: List of Segment objects with timing
            audio_files: List of audio file paths
            total_duration: Total duration of the video
            output_path: Path for output audio file

        Returns:
            Path to dubbed audio file
        """
        print("Creating dubbed audio track...")

        # Create a silent base audio
        silent_path = output_path.parent / "silent_base.wav"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:d={total_duration}",
            "-acodec", "pcm_s16le",
            str(silent_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Build filter complex to overlay segments
        filter_parts = []
        inputs = ["-i", str(silent_path)]

        for i, (segment, audio_file) in enumerate(zip(segments, audio_files)):
            inputs.extend(["-i", str(audio_file)])
            delay_ms = int(segment.start * 1000)
            filter_parts.append(
                f"[{i + 1}]adelay={delay_ms}|{delay_ms}[d{i}]"
            )

        # Mix all delayed audio with the silent base
        mix_inputs = "[0]" + "".join(f"[d{i}]" for i in range(len(segments)))
        filter_parts.append(f"{mix_inputs}amix=inputs={len(segments) + 1}[out]")

        filter_complex = ";".join(filter_parts)

        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-acodec", "libmp3lame",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)

        # Clean up
        silent_path.unlink(missing_ok=True)

        return output_path

    def mix_audio(
        self,
        original_video: Path,
        dubbed_audio: Path,
        output_path: Path,
        original_volume: float = 0.2
    ) -> Path:
        """
        Mix dubbed audio with original video.

        Args:
            original_video: Path to original video file
            dubbed_audio: Path to dubbed audio file
            output_path: Path for output video
            original_volume: Volume level for original audio (0-1)

        Returns:
            Path to output video with dubbed audio
        """
        print("Mixing dubbed audio with video...")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(original_video),
            "-i", str(dubbed_audio),
            "-filter_complex",
            f"[0:a]volume={original_volume}[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2[out]",
            "-map", "0:v",
            "-map", "[out]",
            "-c:v", "copy",
            "-c:a", "aac",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        print(f"Dubbed video saved to: {output_path}")

        return output_path


def get_available_voices(language: str) -> List[str]:
    """Get list of available voices for a language."""
    # This would require edge-tts to fetch voices
    # For now, return the default mapping
    return [VOICE_MAP.get(language, "Unknown")]
