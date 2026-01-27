"""Text translation using deep-translator."""

from typing import List
from deep_translator import GoogleTranslator

from video_traductor.transcriber import Segment


# Supported language codes
SUPPORTED_LANGUAGES = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "pt": "portuguese",
    "it": "italian",
    "ja": "japanese",
    "zh-CN": "chinese (simplified)",
    "ko": "korean",
    "ru": "russian",
    "ar": "arabic",
    "hi": "hindi",
}


class TextTranslator:
    """Translate text using Google Translate API."""

    def __init__(self, source_lang: str = "auto", target_lang: str = "es"):
        """
        Initialize translator.

        Args:
            source_lang: Source language code or 'auto' for detection
            target_lang: Target language code (e.g., 'es', 'en')
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)

    def translate(self, text: str) -> str:
        """
        Translate a single text string.

        Args:
            text: Text to translate

        Returns:
            Translated text
        """
        if not text.strip():
            return text

        return self.translator.translate(text)

    def translate_segments(self, segments: List[Segment]) -> List[Segment]:
        """
        Translate a list of segments preserving timing.

        Args:
            segments: List of Segment objects with text and timing

        Returns:
            List of Segment objects with translated text
        """
        print(f"Translating {len(segments)} segments to {self.target_lang}...")

        translated_segments = []

        for i, segment in enumerate(segments):
            translated_text = self.translate(segment.text)

            translated_segments.append(Segment(
                start=segment.start,
                end=segment.end,
                text=translated_text
            ))

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Translated {i + 1}/{len(segments)} segments")

        return translated_segments

    def translate_batch(self, texts: List[str], batch_size: int = 50) -> List[str]:
        """
        Translate multiple texts efficiently.

        Args:
            texts: List of texts to translate
            batch_size: Number of texts per batch (API limit)

        Returns:
            List of translated texts
        """
        translated = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Join with delimiter, translate, then split
            joined = "\n||||\n".join(batch)
            result = self.translate(joined)
            translated.extend(result.split("\n||||\n"))

        return translated


def get_supported_languages() -> dict:
    """Return dictionary of supported language codes and names."""
    return SUPPORTED_LANGUAGES.copy()
