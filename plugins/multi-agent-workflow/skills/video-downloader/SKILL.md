# Skill: Video Downloader

## Propósito

Descargar videos de YouTube y otras plataformas usando múltiples estrategias para maximizar la compatibilidad en diferentes entornos de red.

## Uso

```bash
# Uso básico
python -m skills.video_downloader "https://youtu.be/VIDEO_ID"

# Con opciones
python -m skills.video_downloader "https://youtu.be/VIDEO_ID" \
    --output ./output \
    --format mp4 \
    --quality 720p \
    --extract-audio
```

## Estrategias de Descarga

El skill intenta múltiples estrategias en orden:

1. **yt-dlp directo** - Método estándar con yt-dlp
2. **yt-dlp con proxy** - Usa proxies públicos si están configurados
3. **yt-dlp con cookies** - Usa cookies de navegador para autenticación
4. **Invidious API** - Usa instancias de Invidious como proxy
5. **Cobalt API** - Usa el servicio cobalt.tools como fallback

## Configuración

Crear archivo `.env` o exportar variables:

```bash
# Proxy opcional
export VIDEO_PROXY="socks5://127.0.0.1:1080"

# Instancia de Invidious preferida
export INVIDIOUS_INSTANCE="https://invidious.snopyta.org"

# Cobalt API
export COBALT_API="https://api.cobalt.tools"
```

## Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `url` | URL del video (requerido) | - |
| `--output`, `-o` | Directorio de salida | `./output` |
| `--format`, `-f` | Formato de salida (mp4, webm, mp3) | `mp4` |
| `--quality`, `-q` | Calidad (360p, 480p, 720p, 1080p, best) | `720p` |
| `--extract-audio` | Solo extraer audio | `false` |
| `--strategy` | Forzar estrategia específica | `auto` |

## Ejemplo de Integración

```python
from skills.video_downloader import VideoDownloaderSkill

skill = VideoDownloaderSkill(output_dir="./downloads")
result = skill.download("https://youtu.be/IpHbbq0O7Wo")

if result.success:
    print(f"Video descargado: {result.video_path}")
    print(f"Audio extraído: {result.audio_path}")
else:
    print(f"Error: {result.error}")
```

## Plataformas Soportadas

- YouTube
- Vimeo
- Twitter/X
- TikTok
- Instagram
- Facebook
- Y más (todo lo que soporte yt-dlp)

## Dependencias

- `yt-dlp` >= 2024.1.0
- `requests` >= 2.28.0
- `ffmpeg` (sistema)

## Notas

- En entornos con restricciones de red (firewalls corporativos, etc.), las estrategias alternativas como Invidious o Cobalt pueden funcionar cuando yt-dlp directo falla.
- Algunas estrategias pueden tener límites de uso o requerir configuración adicional.
