"""Audio transcription using OpenAI Whisper."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import whisper


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
    """Transcribe audio using OpenAI Whisper."""

    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(self, model_size: str = "base"):
        """
        Initialize transcriber with specified model size.

        Args:
            model_size: One of tiny, base, small, medium, large
                       Larger models are more accurate but slower
        """
        if model_size not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model must be one of {self.AVAILABLE_MODELS}")

        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
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

        options = {"task": "transcribe"}
        if language:
            options["language"] = language

        result = self.model.transcribe(str(audio_path), **options)

        segments = [
            Segment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip()
            )
            for seg in result["segments"]
        ]

        return Transcript(
            language=result["language"],
            segments=segments,
            full_text=result["text"].strip()
        )

    def detect_language(self, audio_path: Path) -> str:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        # Load audio and pad/trim to 30 seconds for detection
        audio = whisper.load_audio(str(audio_path))
        audio = whisper.pad_or_trim(audio)

        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # Detect language
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)

        return detected_lang
