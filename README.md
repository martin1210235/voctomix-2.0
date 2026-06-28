# Voctomix 2.0

**Full-HD software live video mixer, extended and containerized for reproducible remote production.**

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![GStreamer](https://img.shields.io/badge/GStreamer-1.20%2B-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5)

Voctomix 2.0 is an evolution of the open-source live video mixing system originally developed by [C3VOC](https://c3voc.de/). It preserves the original client-server architecture, a **voctocore** GStreamer processing engine and a **voctogui** GTK operator interface, and adds a set of production-oriented features together with a complete containerized deployment stack, validated across four real deployment scenarios: single PC, two PCs, Docker Compose and Kubernetes.

The system has been used within the **CyberNEMO** European research project at the Grupo de Aplicación de Telecomunicaciones Visuales (GATV), Universidad Politécnica de Madrid (UPM).

> **Academic context.** This repository contains the software developed for a Bachelor's Thesis (Trabajo Fin de Grado) in Telecommunication Engineering.
> - **Author:** Martín Herranz Sánchez
> - **Institution:** Escuela Técnica Superior de Ingenieros de Telecomunicación (ETSIT), Universidad Politécnica de Madrid (UPM)
> - **Research group / project:** GATV — CyberNEMO
> - **Academic year:** 2025–2026

---

## Table of Contents

- [Overview](#overview)
- [What's New in 2.0](#whats-new-in-20)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [Scenario 1 — Single PC (native)](#scenario-1--single-pc-native)
  - [Scenario 2 — Two PCs (native)](#scenario-2--two-pcs-native)
  - [Scenario 3 — Docker (recommended)](#scenario-3--docker-recommended)
  - [Scenario 4 — Kubernetes](#scenario-4--kubernetes)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Port Reference](#port-reference)
- [Configuration](#configuration)
- [Telemetry JSON Format](#telemetry-json-format)
- [Validation and Reproducibility](#validation-and-reproducibility)
- [Based On](#based-on)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**voctocore** accepts incoming audio/video streams over TCP (Matroska container, UYVY video plus PCM S16LE audio), mixes them through GStreamer's `compositor` element, and exposes the program output on TCP port 15000. It is driven by a line-based text-command interface on TCP port 9999.

**voctogui** is a GTK client that connects to voctocore, renders live previews of every source and of the program mix, and provides the complete operator toolbar (source selection, composite modes, stream blanker, overlays and on-air titling).

The contribution of this work is twofold: a set of production features built on top of the original mixer, and a reproducible deployment methodology that takes the same system from a single workstation to a Kubernetes cluster without changes to the core code.

---

## What's New in 2.0

| Feature | Implementation |
|---|---|
| Stream Blanker (LIVE / PAUSE / NOSTREAM) | `voctocore/lib/streamblanker.py`, `voctogui/lib/toolbar/streamblank.py` |
| Dynamic on-air titling (lower-thirds) | `voctogui/lib/toolbar/overlay.py`, `voctogui/ui/` |
| Telemetry service | `voctogui/lib/gui_state_exporter.py`, `example-scripts/ffmpeg/telemetry_service.py` |
| Audio Follows Video (AFV) | `voctocore/lib/audiomix.py` |
| Auto-off overlays | `voctogui/lib/toolbar/overlay.py` |
| Full container deployment | `Dockerfile`, `docker-compose.yml`, `launch_docker_studio.sh`, `k8s/` |
| Intro / VTR pre-loaded sources | `example-scripts/ffmpeg/auto_launch_intro.sh` |

### Stream Blanker (LIVE / PAUSE / NOSTREAM)
A three-state output control replaces the original binary on/off switch. The operator switches between a live program feed, a branded pause slate with background music, and a full offline screen, without stopping or restarting the pipeline.

### Dynamic on-air titling
Two independent text layers (lower-thirds, speaker names, event titles) are typed in the GUI and composited directly over the live program in real time.

### Telemetry service
A background thread in voctogui exports the complete mixer state (active sources, composite mode, stream blanker status, overlay text and audio levels) as a structured JSON document every second. In single-machine deployments it is written to `registros/gui_state.json`; in multi-machine and containerized deployments it is delivered over HTTP POST to the telemetry service, which exposes an HTTP endpoint on port 8080 and publishes the events to a RabbitMQ broker over AMQP.

### Audio Follows Video
When the operator switches the program source, the audio mix follows automatically: the outgoing source fades out and the incoming source fades in, with no manual action on the audio toolbar.

### Auto-off overlays
Overlays and dynamic titles are dismissed automatically on every cut or composite change, preventing stale on-air graphics from carrying over to the next segment.

### Container deployment
The full production stack (core, sources, stream blanker, telemetry, audio manager and RabbitMQ broker) starts with a single command. Health checks enforce the correct startup order; camera containers share the voctocore network namespace and therefore communicate over loopback without virtual-network overhead.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       voctogui (GTK)                         │
│   Sources A/B · Composites · Blanker · Overlays · Titling    │
└──────────────────────────┬──────────────────────────────────┘
                           │  TCP :9999 (control)
                           │  TCP :14000-14005 (source previews)
┌──────────────────────────▼──────────────────────────────────┐
│                  voctocore  (Python + GStreamer)             │
│                                                              │
│   cam1   :10000 ─┐                                           │
│   cam2   :10001 ─┤                                           │
│   cam3   :10002 ─┼──► compositor ──► stream-blanker ────────►│ :15000  program out
│   cam4   :10003 ─┤                 └────────────────────────►│ :11000  raw mix
│   break  :10004 ─┤                                           │
│   intro  :10005 ─┘                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │       Telemetry / RabbitMQ       │
          │   HTTP :8080  ·  AMQP :5672       │
          └──────────────────────────────────┘
```

A detailed description of the GStreamer pipeline, modules and data flow is provided in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Prerequisites

### Native (Scenarios 1 and 2)

- **Operating system:** Ubuntu 22.04 LTS or Debian Bookworm
- **Python:** 3.10 or newer
- **GStreamer:** 1.20 or newer recommended

```bash
sudo apt install \
    python3 python3-gi python3-gi-cairo python3-scipy python3-numpy \
    gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 gir1.2-gtk-3.0 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    ffmpeg netcat-openbsd iproute2

pip3 install pika==1.3.2
```

### Docker (Scenario 3)

- **Docker:** 24.0 or newer
- **Docker Compose plugin:** v2.20 or newer (`docker compose`, not `docker-compose`)
- A working **X11 display** on the host (voctogui runs natively, not in a container)

```bash
docker compose version   # verify installation
```

### Kubernetes (Scenario 4)

- **Minikube** with a working container runtime
- **kubectl** configured against the local cluster

---

## Quick Start

```bash
git clone https://github.com/martin1210235/voctomix-2.0.git
cd voctomix-2.0
```

> Place the VTR assets in `videos/` before launching:
> `videos/intro.mp4`, `videos/SLIDES_video_starting_soon.mp4`,
> `videos/stream_offline.mp4`, `videos/musica_pausa.mp3`.

### Scenario 1 — Single PC (native)

Runs voctocore, all test sources, the telemetry service, a program monitor and voctogui on one machine.

```bash
./start_studio_single_pc.sh
```

The script auto-detects the LAN IP, cleans up any previous processes, waits for port 9999 to be listening, and then opens the GUI. Closing the GUI window shuts the whole studio down cleanly. A self-contained variant is also available under `1pc_escenario1/`.

### Scenario 2 — Two PCs (native)

**PC 1 (server):** runs voctocore and all sources.

```bash
# Optional: override LAN IP if auto-detection fails
# LOCAL_IP=10.0.0.5 ./2pc_escenario2/start_voctocore_pc1.sh
./2pc_escenario2/start_voctocore_pc1.sh
```

**PC 2 (operator):** runs voctogui pointing at PC 1.

```bash
IP_SERVER=<IP_OF_PC1> ./2pc_escenario2/start_voctogui_pc2.sh
```

Both machines must share a LAN, with the ports in the [Port Reference](#port-reference) reachable between them.

### Scenario 3 — Docker (recommended)

The most reproducible deployment. A single script builds the image, starts all services in order, waits for the health checks to pass, and then opens voctogui on the host.

```bash
# Allow the host GUI to receive the voctogui window
xhost +local:$(id -un)
./launch_docker_studio.sh
```

To override the LAN IP used by the telemetry service: `MI_IP_REAL=10.0.0.5 ./launch_docker_studio.sh`.
Stop the stack with `sudo docker compose down`.

**Services started by `docker compose up`:**

| Container | Role | Exposed ports |
|---|---|---|
| `voctocore` | GStreamer mixer core | 9999, 9998/udp, 10000–10005, 11000, 12000, 13000–13005, 14000–14005, 15000 |
| `rabbitmq` | AMQP message broker | 5672, 15672 (web UI) |
| `telemetry` | GUI-state HTTP endpoint and RabbitMQ publisher | 8080 |
| `cam1`–`cam4` | Synthetic test video sources | internal (share voctocore network) |
| `break` | Break / pause video source | internal |
| `intro` | Intro video loop (port 10005) | internal |
| `stream_blanker` | Blanker video source | internal |
| `audio_manager` | Dynamic audio controller | internal |

### Scenario 4 — Kubernetes

Orchestrated deployment on a local Minikube cluster, mirroring the two-PC roles at the orchestration level.

```bash
# PC 1 (server): starts Minikube, applies the manifests, opens the port-forward
./k8s_escenario/start_server_pc1.sh

# PC 2 (operator): runs voctogui against the forwarded address
./k8s_escenario/start_operator_pc2.sh
```

All containers in the `studio` Pod share a single network namespace (the same loopback pattern used by Docker Compose). RabbitMQ runs as a StatefulSet backed by a PersistentVolumeClaim for queue durability. The complete walkthrough is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Documentation

In-depth documentation is provided in [`docs/`](docs/):

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, GStreamer pipeline, modules, data flow |
| [CONTROL_PROTOCOL.md](docs/CONTROL_PROTOCOL.md) | TCP control protocol (port 9999), full command reference |
| [TELEMETRY.md](docs/TELEMETRY.md) | RabbitMQ AMQP chain, CHANGE/STATE events, JSON schema |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | The four deployment scenarios, step by step |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | `default-config.ini` reference |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Known issues and fixes |

---

## Project Structure

```
voctomix-2.0/
│
├── voctocore/                      # GStreamer mixer server (Python)
│   ├── voctocore.py                # Entry point
│   ├── default-config.ini          # Mix configuration (sources, caps, blanker)
│   └── lib/
│       ├── streamblanker.py        # LIVE/PAUSE/NOSTREAM pipeline
│       ├── audiomix.py             # Audio-Follows-Video logic
│       ├── videomix.py             # GStreamer compositor
│       ├── overlay.py              # Overlay image injection
│       ├── composites.py           # Composite definitions (fs, pip, sbs, lecture)
│       └── controlserver.py        # TCP control protocol (:9999)
│
├── voctogui/                       # GTK operator interface (Python)
│   ├── voctogui.py                 # Entry point
│   ├── default-config.ini          # GUI configuration
│   └── lib/
│       ├── gui_state_exporter.py   # Telemetry JSON exporter
│       └── toolbar/
│           ├── streamblank.py      # Stream status toolbar
│           └── overlay.py          # Dynamic titling and auto-off
│
├── vocto/                          # Shared library (composite command enum)
│
├── example-scripts/ffmpeg/         # Source injection and utility scripts
│   ├── source-testvideo-as-cam*.sh # Synthetic cameras via FFmpeg
│   ├── stream_blanker_source.sh    # Blanker source
│   ├── auto_launch_intro.sh        # Intro VTR watchdog
│   ├── stream-hd-to-youtube.sh     # H.264 stream to YouTube Live
│   ├── record-mixed-ffmpeg.sh      # Program recording
│   ├── telemetry_service.py        # HTTP + RabbitMQ telemetry backend
│   └── audio_control.sh            # Dynamic audio controller
│
├── 1pc_escenario1/                 # Scenario 1: single-PC scripts
├── 2pc_escenario2/                 # Scenario 2: server + operator scripts
├── docker_escenario3/              # Scenario 3: Docker variant scripts
├── k8s/  ·  k8s_escenario/         # Scenario 4: Kubernetes manifests and scripts
│
├── images/                         # Overlay graphics and backgrounds
├── experiments/                    # Measurement scripts and raw logs (reproducibility)
├── tools/                          # Maintenance and release tooling
│
├── Dockerfile                      # Ubuntu 22.04 + GStreamer + FFmpeg + pika
├── docker-compose.yml              # Production stack
├── launch_docker_studio.sh         # Scenario 3: one-command Docker launcher
├── launch_k8s.sh                   # Scenario 4: Kubernetes launcher
├── start_studio_single_pc.sh       # Scenario 1: single-PC native launcher
├── .github/workflows/              # Continuous integration (tests, lint, Docker build)
└── docs/                           # Project documentation
```

---

## Port Reference

| Port | Protocol | Direction | Description |
|------|----------|-----------|-------------|
| 9999 | TCP | → voctocore | Control protocol (text commands) |
| 9998 | UDP | broadcast | GStreamer `GstNetTimeProvider` (A/V sync clock) |
| 10000–10003 | TCP | → voctocore | Camera inputs cam1–cam4 (MKV / UYVY + S16LE) |
| 10004 | TCP | → voctocore | Break / pause source |
| 10005 | TCP | → voctocore | Intro video source |
| 11000 | TCP | ← voctocore | Raw program mix (MKV / UYVY + S16LE) |
| 12000 | TCP | ← voctocore | Mix preview (JPEG / MKV) |
| 13000–13005 | TCP | ← voctocore | Per-source recording outputs |
| 14000–14005 | TCP | ← voctocore | Per-source preview outputs (GUI) |
| 15000 | TCP | ← voctocore | Post-blanker program output (stream feed) |
| 8080 | HTTP | ← telemetry | GUI-state JSON endpoint |
| 5672 | AMQP | ↔ RabbitMQ | Message broker |
| 15672 | HTTP | ← RabbitMQ | RabbitMQ management web UI |

---

## Configuration

voctocore is configured through `voctocore/default-config.ini`. Key sections:

```ini
[mix]
sources = cam1,cam2,cam3,cam4,break,intro
videocaps = video/x-raw,format=UYVY,width=1920,height=1080,framerate=25/1
audiocaps = audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000

[stream-blanker]
enabled = true
sources = pause,nostream   ; drives the PAUSE and NOSTREAM buttons in the GUI
volume = 1.0

[overlay]
path = ./images
auto-off = true
blend-time = 300           ; milliseconds for overlay fade in/out

[previews]
enabled = true
videocaps = video/x-raw,width=1024,height=576,framerate=25/1

[mirrors]
enabled = true
```

Any value defined in the core configuration overrides the GUI's equivalent, keeping all connected GUI instances in sync. The full reference is in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

---

## Telemetry JSON Format

Every second, `GuiStateExporter` publishes a full snapshot of the mixer state. Example:

```json
{
  "last_update": "2026-04-22 14:35:01",
  "gui_ip": "192.168.1.10",
  "preview": { "channel_a": "cam1", "channel_b": "cam2" },
  "mode": "live",
  "composite": {
    "name": "full_screen",
    "fullscreen": true, "side_by_side": false, "pip": false, "lecture": false
  },
  "mirror": false,
  "insertion": {
    "overlay": false, "auto_off": true, "overlay_selected": "logo_event.png",
    "text1_active": true, "text1_value": "Speaker Name", "text2_active": false, "text2_value": ""
  },
  "audio": {
    "cam1_db": -18.5, "cam2_db": -42.0, "cam3_db": null,
    "cam4_db": null, "break_db": null, "intro_db": null
  }
}
```

- **Docker / network mode:** available at `http://localhost:8080/gui_state`
- **Native mode:** written to `registros/gui_state.json`

The complete AMQP event chain and schema are documented in [docs/TELEMETRY.md](docs/TELEMETRY.md).

---

## Validation and Reproducibility

The system was validated across the four deployment scenarios. Resilience was measured as the median time for the program output to recover after an input source disconnects and reconnects:

| Deployment | Median program-recovery time |
|---|---|
| Docker Compose | ≈ 520 ms |
| Kubernetes (Minikube) | ≈ 570 ms |

The measurement scripts and the raw logs behind these figures are kept under [`experiments/`](experiments/) so the results can be reproduced. The complete experimental methodology and the full set of results are reported in the thesis.

---

## Based On

This project is a fork and extension of [voc/voctomix](https://github.com/voc/voctomix) (branch `voctomix2`), originally developed by the C3VOC team. The new features, the container and Kubernetes deployment, the launch scripts and this documentation were developed as part of a Bachelor's Thesis in Telecommunication Engineering (2025–2026).

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup, coding conventions (clean, modular, English-only code and comments), commit-message rules (Conventional Commits) and the test and lint workflow.

Before opening a pull request:

```bash
sh voctocore/test.sh   # voctocore unit tests (mock GI bindings; needs: pip install mock)
sh check_pep8.sh       # pycodestyle lint
```

For setup problems, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## License

Released under the [MIT License](LICENSE.txt).
