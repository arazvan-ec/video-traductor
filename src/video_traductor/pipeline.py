"""Main translation pipeline orchestrating all components."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from video_traductor.downloader import VideoDownloader, DownloadResult
from video_traductor.transcriber import AudioTranscriber, Transcript
from video_traductor.translator import TextTranslator
from video_traductor.subtitles import SubtitleGenerator
from video_traductor.dubbing import VideoDubber


@dataclass
class PipelineResult:
    """Result of translation pipeline."""
    video_title: str
    source_language: str
    target_language: str
    subtitle_path: Path
    dubbed_video_path: Optional[Path] = None
    transcript_original: Optional[str] = None
    transcript_translated: Optional[str] = None


class TranslationPipeline:
    """Orchestrate the full video translation workflow."""

    def __init__(
        self,
        output_dir: Path = Path("output"),
        temp_dir: Path = Path(".tmp"),
        whisper_model: str = "base"
    ):
        """
        Initialize pipeline.

        Args:
            output_dir: Directory for final output files
            temp_dir: Directory for temporary files
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.whisper_model = whisper_model

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        url: str,
        target_lang: str = "es",
        source_lang: Optional[str] = None,
        dub: bool = False,
        keep_temp: bool = False
    ) -> PipelineResult:
        """
        Run the full translation pipeline.

        Args:
            url: YouTube video URL
            target_lang: Target language code (e.g., 'es', 'fr')
            source_lang: Source language code or None for auto-detect
            dub: Whether to generate dubbed audio
            keep_temp: Whether to keep temporary files

        Returns:
            PipelineResult with paths to generated files
        """
        print("=" * 60)
        print("VIDEO TRADUCTOR")
        print("=" * 60)

        try:
            # Step 1: Download video
            print("\n[1/5] Downloading video...")
            downloader = VideoDownloader(self.temp_dir)
            download_result = downloader.download(url)
            print(f"  Title: {download_result.info.title}")
            print(f"  Duration: {download_result.info.duration}s")

            # Step 2: Transcribe audio
            print("\n[2/5] Transcribing audio...")
            transcriber = AudioTranscriber(self.whisper_model)
            transcript = transcriber.transcribe(
                download_result.audio_path,
                language=source_lang
            )
            print(f"  Detected language: {transcript.language}")
            print(f"  Segments: {len(transcript.segments)}")

            # Step 3: Translate text
            print("\n[3/5] Translating to {target_lang}...")
            translator = TextTranslator(
                source_lang=transcript.language,
                target_lang=target_lang
            )
            translated_segments = translator.translate_segments(transcript.segments)

            # Step 4: Generate subtitles
            print("\n[4/5] Generating subtitles...")
            subtitle_gen = SubtitleGenerator()
            safe_title = download_result.info.title.replace(' ', '_')[:50]
            subtitle_path = self.output_dir / f"{safe_title}_{target_lang}.srt"
            subtitle_gen.generate_srt(translated_segments, subtitle_path)

            # Step 5: Optional dubbing
            dubbed_path = None
            if dub:
                print("\n[5/5] Generating dubbed audio...")
                dubber = VideoDubber(language=target_lang)

                # Synthesize speech for each segment
                speech_dir = self.temp_dir / "speech"
                audio_files = dubber.synthesize_speech(translated_segments, speech_dir)

                # Create dubbed audio track
                dubbed_audio = self.temp_dir / "dubbed_audio.mp3"
                dubber.create_dubbed_audio(
                    translated_segments,
                    audio_files,
                    download_result.info.duration,
                    dubbed_audio
                )

                # Mix with original video
                dubbed_path = self.output_dir / f"{safe_title}_{target_lang}_dubbed.mp4"
                dubber.mix_audio(
                    download_result.video_path,
                    dubbed_audio,
                    dubbed_path
                )
            else:
                print("\n[5/5] Skipping dubbing (use --dub to enable)")

            # Build result
            result = PipelineResult(
                video_title=download_result.info.title,
                source_language=transcript.language,
                target_language=target_lang,
                subtitle_path=subtitle_path,
                dubbed_video_path=dubbed_path,
                transcript_original=transcript.full_text,
                transcript_translated="\n".join(s.text for s in translated_segments)
            )

            print("\n" + "=" * 60)
            print("COMPLETED!")
            print("=" * 60)
            print(f"Subtitles: {subtitle_path}")
            if dubbed_path:
                print(f"Dubbed video: {dubbed_path}")

            return result

        finally:
            if not keep_temp:
                self.cleanup()

    def cleanup(self):
        """Remove temporary files."""
        if self.temp_dir.exists():
            print("\nCleaning up temporary files...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)
