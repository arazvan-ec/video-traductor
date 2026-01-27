"""Subtitle generation in SRT format."""

from pathlib import Path
from typing import List
import pysrt

from video_traductor.transcriber import Segment


class SubtitleGenerator:
    """Generate SRT subtitle files."""

    def __init__(self, max_chars_per_line: int = 42, max_lines: int = 2):
        """
        Initialize subtitle generator.

        Args:
            max_chars_per_line: Maximum characters per subtitle line
            max_lines: Maximum lines per subtitle
        """
        self.max_chars_per_line = max_chars_per_line
        self.max_lines = max_lines

    def generate_srt(self, segments: List[Segment], output_path: Path) -> Path:
        """
        Generate SRT file from segments.

        Args:
            segments: List of Segment objects with timing and text
            output_path: Path for output SRT file

        Returns:
            Path to generated SRT file
        """
        subs = pysrt.SubRipFile()

        for i, segment in enumerate(segments):
            # Format text to fit subtitle constraints
            formatted_text = self.format_segment(segment.text)

            sub = pysrt.SubRipItem(
                index=i + 1,
                start=self._seconds_to_time(segment.start),
                end=self._seconds_to_time(segment.end),
                text=formatted_text
            )
            subs.append(sub)

        subs.save(str(output_path), encoding='utf-8')
        print(f"Subtitles saved to: {output_path}")

        return output_path

    def format_segment(self, text: str) -> str:
        """
        Format text to fit subtitle constraints.

        Args:
            text: Raw text to format

        Returns:
            Formatted text with line breaks
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)

            # Check if adding this word exceeds line limit
            if current_length + word_length + 1 > self.max_chars_per_line:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    # Word is longer than max, add it anyway
                    lines.append(word)
                    current_length = 0
            else:
                current_line.append(word)
                current_length += word_length + (1 if current_line else 0)

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        # Limit to max lines
        if len(lines) > self.max_lines:
            lines = lines[:self.max_lines]

        return '\n'.join(lines)

    def _seconds_to_time(self, seconds: float) -> pysrt.SubRipTime:
        """Convert seconds to SubRipTime."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return pysrt.SubRipTime(
            hours=hours,
            minutes=minutes,
            seconds=secs,
            milliseconds=millis
        )


def load_srt(path: Path) -> List[Segment]:
    """
    Load SRT file and convert to Segment list.

    Args:
        path: Path to SRT file

    Returns:
        List of Segment objects
    """
    subs = pysrt.open(str(path))
    segments = []

    for sub in subs:
        start = (
            sub.start.hours * 3600 +
            sub.start.minutes * 60 +
            sub.start.seconds +
            sub.start.milliseconds / 1000
        )
        end = (
            sub.end.hours * 3600 +
            sub.end.minutes * 60 +
            sub.end.seconds +
            sub.end.milliseconds / 1000
        )

        segments.append(Segment(
            start=start,
            end=end,
            text=sub.text.replace('\n', ' ')
        ))

    return segments
