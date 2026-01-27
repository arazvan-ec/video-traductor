"""Command-line interface for video-traductor."""

import argparse
import sys
from pathlib import Path

from video_traductor import __version__
from video_traductor.pipeline import TranslationPipeline
from video_traductor.translator import get_supported_languages


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="video-traductor",
        description="Translate YouTube videos to different languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate to Spanish with subtitles only
  python -m video_traductor https://youtu.be/VIDEO_ID --lang es

  # Translate to French with dubbed audio
  python -m video_traductor https://youtu.be/VIDEO_ID --lang fr --dub

  # Use a larger Whisper model for better accuracy
  python -m video_traductor https://youtu.be/VIDEO_ID --lang es --model medium

Supported languages: es, en, fr, de, pt, it, ja, zh-CN, ko, ru, ar, hi
        """
    )

    parser.add_argument(
        "url",
        help="YouTube video URL"
    )

    parser.add_argument(
        "-l", "--lang",
        default="es",
        help="Target language code (default: es)"
    )

    parser.add_argument(
        "-s", "--source-lang",
        default=None,
        help="Source language code (default: auto-detect)"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output)"
    )

    parser.add_argument(
        "--dub",
        action="store_true",
        help="Generate dubbed audio (slower)"
    )

    parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)"
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files after processing"
    )

    parser.add_argument(
        "--languages",
        action="store_true",
        help="List supported languages and exit"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # List languages if requested
    if args.languages:
        print("Supported languages:")
        for code, name in get_supported_languages().items():
            print(f"  {code}: {name}")
        sys.exit(0)

    # Validate language
    supported = get_supported_languages()
    if args.lang not in supported:
        print(f"Error: Unsupported language '{args.lang}'")
        print(f"Supported languages: {', '.join(supported.keys())}")
        sys.exit(1)

    # Run pipeline
    try:
        pipeline = TranslationPipeline(
            output_dir=args.output,
            whisper_model=args.model
        )

        result = pipeline.run(
            url=args.url,
            target_lang=args.lang,
            source_lang=args.source_lang,
            dub=args.dub,
            keep_temp=args.keep_temp
        )

        print("\nDone!")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
