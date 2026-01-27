"""Audio transcription using faster-whisper."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from faster_whisper import WhisperModel


@dataclass
class Segment:
    """A transcribed segment with timing."""
    start: float  # seconds
    end: float    # seconds
    text: str


@dataclass
class Transcript:
    """Full transcription result."""
    language: str
    segments: List[Segment]
    full_text: str


class AudioTranscriber:
    """Transcribe audio using faster-whisper."""

    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]

    def __init__(self, model_size: str = "base"):
        """
        Initialize transcriber with specified model size.

        Args:
            model_size: One of tiny, base, small, medium, large-v2, large-v3
                       Larger models are more accurate but slower
        """
        # Map old model names to new ones
        if model_size == "large":
            model_size = "large-v2"

        if model_size not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model must be one of {self.AVAILABLE_MODELS}")

        print(f"Loading Whisper model: {model_size}")
        # Use CPU with int8 for faster inference without GPU
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.model_size = model_size

    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> Transcript:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es') or None for auto-detect

        Returns:
            Transcript with segments and detected language
        """
        print(f"Transcribing: {audio_path}")

        # Transcribe with faster-whisper
        segments_gen, info = self.model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5
        )

        # Convert generator to list of Segment objects
        segments = []
        full_text_parts = []

        for seg in segments_gen:
            segments.append(Segment(
                start=seg.start,
                end=seg.end,
                text=seg.text.strip()
            ))
            full_text_parts.append(seg.text.strip())

        return Transcript(
            language=info.language,
            segments=segments,
            full_text=" ".join(full_text_parts)
        )

    def detect_language(self, audio_path: Path) -> str:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        # Transcribe a small portion to detect language
        _, info = self.model.transcribe(str(audio_path), beam_size=1)
        return info.language
