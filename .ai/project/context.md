# Video Traductor - Contexto del Proyecto

## Propósito

Video Traductor es una herramienta CLI que permite traducir videos de YouTube a diferentes idiomas. El flujo principal es:

1. **Descarga**: Obtener el video de YouTube usando `yt-dlp`
2. **Extracción de audio**: Separar el audio del video con `ffmpeg`
3. **Transcripción**: Convertir audio a texto usando OpenAI Whisper (modelo local)
4. **Traducción**: Traducir el texto al idioma destino
5. **Generación de subtítulos**: Crear archivo SRT con los subtítulos traducidos
6. **Opcional - Doblaje**: Generar audio con TTS y mezclarlo con el video

## Usuarios Objetivo

- Creadores de contenido que quieren traducir sus videos
- Usuarios que quieren ver videos en su idioma nativo
- Educadores que necesitan material en diferentes idiomas

## Arquitectura

```
video-traductor/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── downloader.py       # Descarga de YouTube
│   ├── transcriber.py      # Transcripción con Whisper
│   ├── translator.py       # Traducción de texto
│   ├── subtitles.py        # Generación de SRT
│   └── dubbing.py          # Doblaje con TTS (opcional)
├── tests/
├── output/                  # Videos/subtítulos procesados
└── .tmp/                    # Archivos temporales
```

## Decisiones Técnicas

1. **Whisper Local vs API**: Usamos Whisper local para evitar costos y límites de API
2. **deep-translator**: Soporta múltiples backends (Google, DeepL, etc.)
3. **ffmpeg-python**: Wrapper Pythonic para operaciones de audio/video
4. **CLI con argparse**: Simple y sin dependencias adicionales

## Limitaciones Conocidas

- Videos muy largos (>2h) pueden requerir mucha RAM para Whisper
- La calidad del TTS varía según el idioma
- Algunos videos de YouTube pueden tener restricciones de descarga
