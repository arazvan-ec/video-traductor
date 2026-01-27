# Video Traductor

Herramienta CLI para traducir videos de YouTube a diferentes idiomas. Genera subtítulos traducidos y opcionalmente audio doblado.

## Características

- **Descarga de YouTube**: Descarga videos usando yt-dlp
- **Transcripción automática**: Convierte audio a texto con OpenAI Whisper (local)
- **Traducción**: Traduce a 12+ idiomas usando Google Translate
- **Subtítulos SRT**: Genera subtítulos sincronizados
- **Doblaje opcional**: Genera audio doblado con edge-tts

## Instalación

### Requisitos previos

- Python 3.11+
- ffmpeg instalado en el sistema

```bash
# Instalar ffmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# Instalar ffmpeg (macOS)
brew install ffmpeg
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Traducir video con subtítulos

```bash
python -m video_traductor https://youtu.be/VIDEO_ID --lang es
```

### Traducir con audio doblado

```bash
python -m video_traductor https://youtu.be/VIDEO_ID --lang es --dub
```

### Opciones

```
usage: video-traductor [-h] [-l LANG] [-s SOURCE_LANG] [-o OUTPUT] [--dub]
                       [-m {tiny,base,small,medium,large}] [--keep-temp]
                       [--languages] [-v]
                       url

Translate YouTube videos to different languages

positional arguments:
  url                   YouTube video URL

options:
  -h, --help            show this help message and exit
  -l, --lang LANG       Target language code (default: es)
  -s, --source-lang     Source language code (default: auto-detect)
  -o, --output OUTPUT   Output directory (default: output)
  --dub                 Generate dubbed audio (slower)
  -m, --model MODEL     Whisper model size: tiny, base, small, medium, large
  --keep-temp           Keep temporary files after processing
  --languages           List supported languages and exit
  -v, --version         show program's version number and exit
```

## Idiomas soportados

| Código | Idioma |
|--------|--------|
| es | Español |
| en | Inglés |
| fr | Francés |
| de | Alemán |
| pt | Portugués |
| it | Italiano |
| ja | Japonés |
| zh-CN | Chino (Simplificado) |
| ko | Coreano |
| ru | Ruso |
| ar | Árabe |
| hi | Hindi |

## Ejemplos

```bash
# Traducir a español (solo subtítulos)
python -m video_traductor https://youtu.be/IpHbbq0O7Wo --lang es

# Traducir a francés con mejor precisión
python -m video_traductor https://youtu.be/IpHbbq0O7Wo --lang fr --model medium

# Traducir con doblaje
python -m video_traductor https://youtu.be/IpHbbq0O7Wo --lang es --dub
```

## Arquitectura

```
video-traductor/
├── src/video_traductor/
│   ├── cli.py          # Interfaz de línea de comandos
│   ├── downloader.py   # Descarga de YouTube
│   ├── transcriber.py  # Transcripción con Whisper
│   ├── translator.py   # Traducción de texto
│   ├── subtitles.py    # Generación de SRT
│   ├── dubbing.py      # Doblaje con TTS
│   └── pipeline.py     # Orquestación
├── tests/
├── output/             # Archivos generados
└── .tmp/               # Archivos temporales
```

## Desarrollo

Este proyecto usa el sistema de workflows del repositorio [arazvan-ec/workflow](https://github.com/arazvan-ec/workflow).

### Ejecutar tests

```bash
pytest tests/
```

### Linting

```bash
ruff check src/
black src/
```

## Licencia

MIT
