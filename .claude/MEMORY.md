# MEMORY.md — Project Context for Claude Code

This file stores persistent context about this project so that any new Claude Code session can get up to speed immediately.

---

## What This Project Is

**Voctomix 2.0** — Bachelor's Thesis (TFG) at ETSIT, Universidad Politécnica de Madrid.

An extension and full containerization of the open-source live video mixer [Voctomix](https://github.com/voc/voctomix) by C3VOC. Real use case: the **CyberNemo group at UPM**, who produce live remote events.

**Stack:** Python 3, GStreamer 1.20+, GTK 3, FFmpeg, Bash, Docker, RabbitMQ, Kubernetes (minikube)

---

## System Architecture

```
voctogui (GTK)  ←→  TCP :9999 (control)  ←→  voctocore (GStreamer)
                 ←  TCP :14000-14005 (source previews)
```

### Port Reference

| Port | Service |
|------|---------|
| 9999 | Control TCP (commands) |
| 9998 | UDP GStreamer clock |
| 10000-10003 | cam1-cam4 inputs |
| 10004 | break source |
| 10005 | intro source |
| 11000 | raw mix output |
| 12000 | mix preview (JPEG) |
| 13000-13005 | per-source mirrors |
| 14000-14005 | per-source previews (GUI) |
| 15000 | program output (post stream-blanker) |
| 17000 | PAUSE video source |
| 17001 | NOSTREAM video source |
| 18000 | background audio |
| 8080 | Telemetry REST API |
| 5672 / 15672 | RabbitMQ (AMQP / web UI) |

### Key voctocore modules

- `voctocore/lib/videomix.py` + `composites.py` — compositor: fullscreen, PIP, side-by-side, lecture, lecture_4:3
- `voctocore/lib/audiomix.py` — Audio Follows Video (auto-fade on source switch)
- `voctocore/lib/streamblanker.py` — LIVE / PAUSE / NOSTREAM three-state output
- `voctocore/lib/overlay.py` — real-time PNG/text overlay injection
- `voctocore/lib/commands.py` + `controlserver.py` — TCP line-based protocol

### Key voctogui modules

- `voctogui/lib/gui_state_exporter.py` — Telemetry: JSON mixer state every 1s → `registros/gui_state.json` or HTTP POST to :8080
- `voctogui/lib/toolbar/streamblank.py` — LIVE/PAUSE/NOSTREAM buttons
- `voctogui/lib/toolbar/overlay.py` — dynamic lower-thirds + auto-off on cut

### Docker stack (docker-compose.yml — 10 services)

voctocore, rabbitmq, telemetry, cam1-cam4, stream_blanker, intro, audio_manager.
Camera containers use `network_mode: service:voctocore` (shared network namespace).

---

## Thesis Structure (approved by tutor 2026-04-22)

### Cap. 1 — Introducción y objetivos
- 1.1 Introducción (caso de uso CyberNemo UPM)
- 1.2 Objetivos
- 1.3 Estructura

### Cap. 2 — Estado del arte
- 2.1 Producción audiovisual (tradicional vs remota)
- 2.2 Contribución de vídeo (SDI, SMPTE 2022/2110, codecs RAW, Matroska)
- 2.3 Distribución de contenidos (protocolos, H.264/H.265, formatos)
- 2.4 Mezclador de vídeo (HW tradicional vs software: OBS, Voctomix)
- *Eliminados: secciones separadas de GStreamer, Docker (integradas en cap.3)*

### Cap. 3 — Diseño e implementación (LaTeX files in `memoria_tfg/capitulos/cap3/`)

**Bloque A — Extensiones al pipeline voctocore:**
- 3.1 Arquitectura del sistema (`3_1_arquitectura.tex`)
- 3.2 Fuentes de señal de cámaras (`3_2_fuentes_camaras.tex`)
- 3.3 Fuentes auxiliares y stream blanker (`3_3_fuentes_auxiliares.tex`)
- 3.4 Modos de composición (`3_4_composites.tex`)
- 3.5 Transiciones (`3_5_transiciones.tex`)
- 3.6 Overlays, logos y texto dinámico (`3_6_overlays_logos_texto.tex`)

**Bloque B — Infraestructura y servicios:**
- 3.7 Personalización de voctogui (`3_7_personalizacion_gui.tex`) — CSS dark theme, SVG, reloj, widgets fantasma
- 3.8 Sistema de telemetría (`3_4_telemetria_notario.tex`) — NO usar la palabra "Notario"
- 3.9 Contenerización Docker (`3_7_contenerizacion_docker.tex`)
- 3.10 Despliegue en Kubernetes (`k8s_escenario/` + `launch_k8s.sh`)

### Cap. 4 — Pruebas de validación
- 4.1 Escenarios de despliegue (2PCs + Docker)
- 4.2 Pruebas de validación (latencia, logs RabbitMQ, screenshots)

### Cap. 5 — Conclusiones y líneas futuras
- 5.2 Líneas futuras: cámaras reales en CyberNemo, interfaz web, NDI
- *Kubernetes ya NO está en líneas futuras — está implementado en cap.3*

---

## Academic Writing Rules

- **Language:** Spanish (thesis), English (code, commits, scientific paper)
- **Style:** No dashes (— or -) for parenthetical remarks → use commas instead
- **Tone:** Academic, objective, third person / plural of modesty
- **Sources:** Prioritize IEEE, academic papers (Google Scholar), RFCs, ISO/SMPTE standards
- Use tables, figures, and diagrams whenever they add clarity

---

## Scientific Paper

- **File**: `paper/template.tex` — git remote points to Overleaf (push/pull to sync)
- **Journal**: Electronics (MDPI), numbered citations [N], target 15–20 pages
- **Full style guide**: `.claude/paper_guide.md` — read before writing anything in the paper
- **Reference paper**: `referencias/paper_voctomix1.0_sofia.pdf` (Electronics 2025, 14, 4115) — same journal, uses Voctomix v1.3 as Production Core component, mandatory citation
- **Overleaf sync**: `cd paper && git pull` / `git push`

---

## Commit Convention

Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, etc.
Messages in English. Explain *what* and *why*, not just *how*.
