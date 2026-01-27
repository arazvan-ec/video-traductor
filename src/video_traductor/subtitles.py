"""Subtitle generation in SRT format."""

from pathlib import Path
from typing import List

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
        srt_content = []

        for i, segment in enumerate(segments):
            # Format text to fit subtitle constraints
            formatted_text = self.format_segment(segment.text)

            # Create SRT entry
            start_time = self._seconds_to_srt_time(segment.start)
            end_time = self._seconds_to_srt_time(segment.end)

            srt_entry = f"{i + 1}\n{start_time} --> {end_time}\n{formatted_text}\n"
            srt_content.append(srt_entry)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

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

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def load_srt(path: Path) -> List[Segment]:
    """
    Load SRT file and convert to Segment list.

    Args:
        path: Path to SRT file

    Returns:
        List of Segment objects
    """
    segments = []

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newline to get entries
    entries = content.strip().split('\n\n')

    for entry in entries:
        lines = entry.strip().split('\n')
        if len(lines) >= 3:
            # Parse timestamp line
            time_line = lines[1]
            start_str, end_str = time_line.split(' --> ')

            start = _parse_srt_time(start_str)
            end = _parse_srt_time(end_str)
            text = ' '.join(lines[2:])

            segments.append(Segment(
                start=start,
                end=end,
                text=text
            ))

    return segments


def _parse_srt_time(time_str: str) -> float:
    """Parse SRT timestamp to seconds."""
    # Format: HH:MM:SS,mmm
    time_str = time_str.strip()
    parts = time_str.replace(',', ':').split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    millis = int(parts[3])

    return hours * 3600 + minutes * 60 + seconds + millis / 1000
