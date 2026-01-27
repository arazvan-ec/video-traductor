# Tareas: Video Translation

## Backend Tasks

### BE-001: Implementar VideoDownloader
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Metodología**: TDD
- **Criterios de Aceptación**:
  - [ ] Descargar video de YouTube dado URL
  - [ ] Extraer metadata (título, duración, etc.)
  - [ ] Extraer audio a formato WAV
  - [ ] Manejar errores de red y videos no disponibles
  - [ ] Tests unitarios con mocks

### BE-002: Implementar AudioTranscriber
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Metodología**: TDD
- **Criterios de Aceptación**:
  - [ ] Cargar modelo Whisper (configurable: tiny, base, small, medium)
  - [ ] Transcribir audio a texto con timestamps
  - [ ] Detectar idioma automáticamente
  - [ ] Retornar segmentos con start/end/text
  - [ ] Tests con archivo de audio de prueba

### BE-003: Implementar TextTranslator
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Metodología**: TDD
- **Criterios de Aceptación**:
  - [ ] Traducir texto usando deep-translator
  - [ ] Soportar múltiples idiomas destino
  - [ ] Traducir lista de segmentos preservando timestamps
  - [ ] Manejar límites de caracteres de la API
  - [ ] Tests con textos de ejemplo

### BE-004: Implementar SubtitleGenerator
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Metodología**: TDD
- **Criterios de Aceptación**:
  - [ ] Generar archivo SRT válido
  - [ ] Formatear líneas a máximo 42 caracteres
  - [ ] Dividir subtítulos largos en múltiples líneas
  - [ ] Sincronizar con timestamps originales
  - [ ] Tests de formato SRT

### BE-005: Implementar VideoDubber (Opcional)
- **Prioridad**: Media
- **Estimación**: 1 checkpoint
- **Metodología**: TDD
- **Criterios de Aceptación**:
  - [ ] Sintetizar voz usando edge-tts
  - [ ] Generar audio para cada segmento
  - [ ] Concatenar segmentos de audio
  - [ ] Mezclar con video original
  - [ ] Tests de integración

### BE-006: Implementar TranslationPipeline
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Metodología**: Integration
- **Criterios de Aceptación**:
  - [ ] Orquestar todos los componentes
  - [ ] Manejar archivos temporales
  - [ ] Limpiar recursos al terminar
  - [ ] Reportar progreso
  - [ ] Tests de integración end-to-end

## CLI Tasks

### CLI-001: Implementar CLI con argparse
- **Prioridad**: Alta
- **Estimación**: 1 checkpoint
- **Criterios de Aceptación**:
  - [ ] Comando `translate` con argumentos requeridos
  - [ ] Opciones: --lang, --output, --dub, --model
  - [ ] Mensajes de ayuda descriptivos
  - [ ] Validación de argumentos
  - [ ] Barra de progreso

## QA Tasks

### QA-001: Tests de Integración
- **Prioridad**: Alta
- **Criterios de Aceptación**:
  - [ ] Test end-to-end con video de prueba corto
  - [ ] Verificar formato SRT generado
  - [ ] Verificar audio doblado (si aplica)

### QA-002: Documentación
- **Prioridad**: Media
- **Criterios de Aceptación**:
  - [ ] README con instrucciones de instalación
  - [ ] Ejemplos de uso
  - [ ] Documentación de API
