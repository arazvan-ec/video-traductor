# Arquitectura: Video Translation

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      cli.py                                  ││
│  │  - parse_args()                                              ││
│  │  - main()                                                    ││
│  │  - TranslateCommand                                          ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Core Services                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ downloader   │  │ transcriber  │  │ translator   │          │
│  │              │  │              │  │              │          │
│  │ - download() │  │ - transcribe │  │ - translate()│          │
│  │ - get_info() │  │ - detect_lang│  │ - batch()    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ subtitles    │  │ dubbing      │  │ pipeline     │          │
│  │              │  │              │  │              │          │
│  │ - generate() │  │ - synthesize │  │ - run()      │          │
│  │ - format()   │  │ - mix_audio()│  │ - cleanup()  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Dependencies                        │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ yt-dlp   │  │ whisper  │  │ ffmpeg   │  │ edge-tts │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
YouTube URL
    │
    ▼
┌─────────────┐
│ Downloader  │──► video.mp4, metadata.json
└─────────────┘
    │
    ▼
┌─────────────┐
│ FFmpeg      │──► audio.wav
└─────────────┘
    │
    ▼
┌─────────────┐
│ Transcriber │──► transcript.json (text + timestamps)
└─────────────┘
    │
    ▼
┌─────────────┐
│ Translator  │──► translated_transcript.json
└─────────────┘
    │
    ├─────────────────────┐
    ▼                     ▼
┌─────────────┐    ┌─────────────┐
│ Subtitles   │    │ Dubbing     │
│ Generator   │    │ (optional)  │
└─────────────┘    └─────────────┘
    │                     │
    ▼                     ▼
output.srt          output_dubbed.mp4
```

## Estructura de Directorios

```
video-traductor/
├── src/
│   └── video_traductor/
│       ├── __init__.py
│       ├── __main__.py        # Entry point
│       ├── cli.py             # Argumentos y comandos
│       ├── downloader.py      # Descarga de YouTube
│       ├── transcriber.py     # Whisper integration
│       ├── translator.py      # Traducción
│       ├── subtitles.py       # Generación SRT
│       ├── dubbing.py         # TTS y mezcla audio
│       ├── pipeline.py        # Orquestación
│       └── utils.py           # Utilidades comunes
├── tests/
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_transcriber.py
│   ├── test_translator.py
│   ├── test_subtitles.py
│   └── conftest.py            # Fixtures pytest
├── output/                     # Archivos generados
├── .tmp/                       # Archivos temporales
├── requirements.txt
├── setup.py
└── README.md
```

## Interfaces de Módulos

### downloader.py
```python
class VideoDownloader:
    def download(self, url: str, output_dir: Path) -> DownloadResult
    def get_info(self, url: str) -> VideoInfo
    def extract_audio(self, video_path: Path) -> Path
```

### transcriber.py
```python
class AudioTranscriber:
    def __init__(self, model_size: str = "base")
    def transcribe(self, audio_path: Path, language: str = None) -> Transcript
    def detect_language(self, audio_path: Path) -> str
```

### translator.py
```python
class TextTranslator:
    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> str
    def translate_segments(self, segments: List[Segment], target_lang: str) -> List[Segment]
```

### subtitles.py
```python
class SubtitleGenerator:
    def generate_srt(self, segments: List[Segment], output_path: Path) -> Path
    def format_segment(self, segment: Segment, max_chars: int = 42) -> List[str]
```

### dubbing.py
```python
class VideoDubber:
    def synthesize_speech(self, segments: List[Segment], lang: str) -> Path
    def mix_audio(self, original_video: Path, dubbed_audio: Path, output: Path) -> Path
```

### pipeline.py
```python
class TranslationPipeline:
    def run(self, url: str, target_lang: str, dub: bool = False) -> PipelineResult
    def cleanup(self) -> None
```
