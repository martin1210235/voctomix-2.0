# GLOSSARY.md — Glosario Técnico del Proyecto

Terminología clave de Voctomix 2.0 para mantener consistencia en código, commits y memoria TFG.

---

## Conceptos Principales

### voctocore
Núcleo multimedia del sistema. Pipeline GStreamer (Python) que mezcla múltiples fuentes de vídeo y audio en tiempo real. Escucha comandos TCP en puerto 9999.

### voctogui
Interfaz gráfica de control (GTK 3, Python). Se conecta a `voctocore` en puerto 9999 para enviar comandos y recibe previews en 14000-14005.

### Compositor (Compositor de vídeo)
Módulo `lib/videomix.py` de voctocore que selecciona y mezcla las fuentes según el modo de composición activo.

---

## Modos de Composición

### fullscreen
Una sola fuente (A o B) a pantalla completa (1920×1080).

### picture-in-picture (PIP)
Fuente A grande (1600×1200) + fuente B pequeña (320×240) en esquina inferior derecha.

### side-by-side (SxS)
Dos fuentes lado a lado (960×1080 cada una). Comúnmente llamado "split screen".

### lecture
Presentador grande (1280×1080) + pantalla compartida pequeña (640×1080) lado a lado.

### lecture_4:3
Variante de lecture optimizada para contenido 4:3. Eliminada la distorsión por crop del 31%.

---

## Fuentes de Entrada

### cam1, cam2, cam3, cam4
Cámaras principales. Se conectan en puertos TCP 10000-10003 respectivamente. Formato esperado: UYVY 1920×1080 @ 25fps, audio 48kHz S16LE estéreo.

### break
Vídeo de descanso/pausa. Puerto 10004. Reproduce bucle de pausa mientras no hay programa en vivo.

### intro
Vídeo de introducción/cabecera. Puerto 10005. Se reproduce automáticamente al iniciar (vigilante_intro.py).

---

## Controles de Salida

### Stream Blanker
Módulo `lib/streamblanker.py`. Controla el estado de la salida con tres estados:

- **LIVE** — programa en vivo (stream 15000 activo)
- **PAUSE** — pausa con música (loop de pausa desde puerto 17000)
- **NOSTREAM** — fuera de aire completo (loop offline desde puerto 17001)

### Audio Follows Video (AFV)
Módulo `lib/audiomix.py`. Cuando el operador cambia de fuente, el audio cambia automáticamente con fade in/out. Elimina la necesidad de ajustes manuales de audio.

### Overlay
PNG que se superpone en tiempo real sobre la mezcla (logos, gráficos estáticos). Inyectado por `lib/overlay.py`.

### Rotulación Dinámica
Texto en tiempo real (lower-thirds, nombres de speakers, títulos). Se inserta mediante GStreamer textoverlay + pipeline de transformación. **Máx. 4 capas** de texto simultáneo.

### Auto-Off (Auto-desaparición)
Característica: overlays y títulos desaparecen automáticamente en cada corte o cambio de compositor. Previene gráficos obsoletos en pantalla.

---

## Telemetría y Monitorización

### Notario
**NO USAR ESTA PALABRA EN LA MEMORIA DEL TFG.** Sistema de telemetría que exporta el estado completo del mezclador (fuentes activas, modo compositor, estado blanker, texto overlay, niveles de audio) como JSON cada 1 segundo.

### gui_state_exporter
Clase en `voctogui/lib/gui_state_exporter.py`. Recorre la GUI, extrae el estado actual y lo exporta en JSON.

### Telemetry Service (o "servicio de telemetría")
Contenedor Docker que recibe JSON via HTTP POST (puerto 8080), lo almacena y lo publica a RabbitMQ (5672 AMQP).

### JSON Lines
Formato: cada línea es un objeto JSON completo (sin saltos dentro). Facilita streaming y lectura incremental.

---

## Infraestructura y Despliegue

### Docker Compose Stack
Configuración en `docker-compose.yml`. 10 servicios: voctocore, voctogui, rabbitmq, telemetry, 4 cámaras, stream_blanker, intro, audio_manager.

### Health Check
Verificación automática de salud de un servicio. Ej: `nc -z localhost 9999` comprueba si voctocore está listo.

### Shared Network Namespace
Modo Docker `network_mode: service:voctocore`. Los contenedores de cámaras comparten la red de voctocore → comunicación localhost sin overhead de red virtual.

### Escenario 1 (Scenario 1)
Despliegue en 1 PC con todo nativo (Python + GStreamer instalados). Script: `start_studio_single_pc.sh`.

### Escenario 2 (Scenario 2)
Despliegue en 2 PCs: uno ejecuta voctocore, otro ejecuta voctogui. Se comunican por red TCP. Scripts: `2pc_escenario2/start_voctocore_pc1.sh` y `start_voctogui_pc2.sh`.

### Escenario 3 (Scenario 3)
Despliegue completo en Docker. Script: `launch_docker_studio.sh`.

### Kubernetes (K8s)
Orquestación de contenedores (producción). Manifiestos en `k8s_escenario/` (studio.yaml, rabbitmq.yaml, etc.). Usado con minikube para desarrollo.

---

## Protocolos y Comunicación

### TCP :9999 (Control Protocol)
Protocolo de línea (line-based). Comandos como `set_video_a cam1`, `get_composite_mode`, `set_stream_blanker_off`, etc. Implementado en `voctocore/lib/commands.py`.

### AMQP (Advanced Message Queuing Protocol)
Protocolo de mensajería. RabbitMQ (puerto 5672) lo implementa. Usado para telemetría y eventos entre servicios.

### SMPTE 2022-6
Estándar de transporte de audio AES sobre IP (redes Ethernet). Relevante para entrada de cámaras profesionales SDI-over-IP.

### H.264 / H.265 (HEVC)
Codecs de vídeo comprimido. H.264 ampliamente soportado; H.265 (HEVC) más eficiente pero menos compatible.

### UYVY
Formato de píxel sin comprimir (YUV 4:2:2 empaquetado). Estándar en entrada de cámaras profesionales SDI.

### S16LE
Formato de audio: 16-bit signed linear PCM, little-endian. 48kHz es estándar de vídeo profesional.

---

## Archivos y Directorios Clave

### voctocore/
Núcleo del mixer. Python + GStreamer.

### voctocore/lib/
Módulos Python: videomix.py, audiomix.py, streamblanker.py, overlay.py, commands.py, pipeline.py, config.py, etc.

### voctocore/tests/
Tests unitarios. Subdirs: `commands/`, `videomix/`, `helper/`. Ejecutar con `./test.sh` o `python3 -m unittest`.

### voctogui/
Interfaz gráfica (GTK 3).

### example-scripts/ffmpeg/
Helpers: scripts para cámaras sintéticas, blanker, intro, YouTube streaming, grabación, telemetry_service.py, audio_control.sh.

### memoria_tfg/
Tesis en LaTeX (español). Caps en `capitulos/cap1/`, `cap2/`, `cap3/`, `cap4/`, `cap5/`.

### registros/
Directorio de salida para JSON de telemetría (se crea en runtime).

### k8s_escenario/
Manifiestos Kubernetes (YAML) y script launch_k8s.sh.

### docker-compose.yml
Definición de servicios Docker.

---

## Convenciones de Commit

### feat:
Nueva característica. Ej: `feat(overlay): add auto-off on composite change`

### fix:
Solución de bug. Ej: `fix(audiomix): correct fade duration on source switch`

### refactor:
Mejora de código sin cambio de funcionalidad. Ej: `refactor(videomix): simplify composite selection logic`

### docs:
Cambios en documentación o memoria LaTeX. Ej: `docs(cap3): rewrite architecture section`

### chore:
Tareas administrativas (dependencias, CI/CD). Ej: `chore: update docker base image`

---

## Acrónimos y Abreviaturas

| Acrónimo | Significado |
|----------|-------------|
| **AFV** | Audio Follows Video |
| **AMQP** | Advanced Message Queuing Protocol |
| **AES** | Audio Engineering Society |
| **API** | Application Programming Interface |
| **BT.709** | Rec. ITU-R BT.709 (colorimetry estándar de vídeo) |
| **C3VOC** | Chaos Computer Club - Video Operation Center |
| **FFmpeg** | Framework multimedia para codificación/decodificación |
| **GI** | GObject Introspection (bindings Python para GStreamer) |
| **GStreamer** | Framework de procesamiento multimedia |
| **GTK** | GIMP Toolkit (framework GUI) |
| **HEVC** | High Efficiency Video Coding (H.265) |
| **IP** | Internet Protocol |
| **JSON** | JavaScript Object Notation |
| **K8s** | Kubernetes |
| **MQTT** | Message Queuing Telemetry Transport |
| **NDI** | Network Device Interface (Vizrt) |
| **OBS** | Open Broadcaster Software |
| **PIP** | Picture-in-Picture |
| **RabbitMQ** | Message broker (AMQP) |
| **REST** | Representational State Transfer |
| **RFC** | Request for Comments (estándares IETF) |
| **RTP** | Real-time Transport Protocol |
| **SDI** | Serial Digital Interface (conexión profesional de vídeo) |
| **SMPTE** | Society of Motion Picture and Television Engineers |
| **SxS** | Side-by-Side |
| **TCP** | Transmission Control Protocol |
| **TFG** | Trabajo Fin de Grado |
| **UDP** | User Datagram Protocol |
| **UPM** | Universidad Politécnica de Madrid |
| **UYVY** | Formato de píxel YUV 4:2:2 empaquetado |
| **VTR** | Video Tape Recorder (aquí: pre-loaded video sources) |
| **YUV** | Color space: luminancia (Y) + crominancia (U, V) |

---

## Notas para Claude Code

Este fichero es **vivo**. Actualízalo cuando:
- Descubras nuevos términos que causen confusión
- Cambien definiciones de módulos existentes
- Se añadan nuevos acrónimos
- El usuario o la memoria indiquen una aclaración necesaria

**Idioma:** Español para definiciones, términos técnicos en inglés (como aparecen en el código).
