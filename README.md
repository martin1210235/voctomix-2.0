# Voctomix 2.0

> **Full-HD Software Live Video Mixer** — extended and containerized as part of a Bachelor's Thesis (TFG) in Engineering.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![GStreamer](https://img.shields.io/badge/GStreamer-1.20%2B-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Status](https://img.shields.io/badge/status-active-success)

Voctomix 2.0 is an evolution of the open-source live video mixing system originally developed by [C3VOC](https://c3voc.de/). It follows the same client-server architecture — a **voctocore** GStreamer processing engine and a **voctogui** GTK operator interface — and adds a set of production-focused features plus a complete Docker deployment stack, validated across four real deployment scenarios (single PC, two PCs, Docker Compose and Kubernetes).

> **Used in production** within the **CyberNEMO** European research project at Universidad Politécnica de Madrid (UPM).

### Quick Links

- 📖 **[Full documentation](docs/)** — architecture, control protocol, telemetry, deployment
- 🏗️ [Architecture](docs/ARCHITECTURE.md) · 🎛️ [Control protocol](docs/CONTROL_PROTOCOL.md) · 📡 [Telemetry](docs/TELEMETRY.md)
- 🤝 [Contributing](CONTRIBUTING.md) · 🗒️ [Changelog](CHANGELOG.md) · ⚖️ [License](LICENSE.txt)

---

## Table of Contents

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
- [Telemetry JSON format](#telemetry-json-format)
- [Contributing](#contributing)
- [License](#license)

---

## What's New in 2.0

| Feature | Files |
|---|---|
| **Stream Blanker — LIVE / PAUSE / NOSTREAM** | `voctocore/lib/streamblanker.py`, `voctogui/lib/toolbar/streamblank.py` |
| **Dynamic on-air titling (lower-thirds)** | `voctogui/lib/toolbar/overlay.py`, `voctogui/ui/` |
| **Telemetry service** | `voctogui/lib/gui_state_exporter.py`, `example-scripts/ffmpeg/telemetry_service.py` |
| **Audio Follows Video (AFV)** | `voctocore/lib/audiomix.py` |
| **Auto-Off Overlays** | `voctogui/lib/toolbar/overlay.py` |
| **Full Docker containerization** | `Dockerfile`, `docker-compose.yml`, `launch_docker_studio.sh` |
| **Intro / VTR pre-loaded sources** | `example-scripts/ffmpeg/auto_launch_intro.sh` |

### Stream Blanker — LIVE / PAUSE / NOSTREAM
Three-state output control replaces the original binary on/off switch. The operator switches between a live program feed, a branded pause slate with background music, and a full offline screen — without stopping or restarting the pipeline.

### Dynamic On-Air Titling
Two independent text layers (lower-thirds, speaker names, event titles) can be typed in the GUI and applied to the live program in real time. Text is composited directly over the output mix.

### Telemetry Service
A background thread in voctogui exports the complete mixer state — active sources, composite mode, stream blanker status, overlay text, audio levels — as a structured JSON document every second. In single-machine setups it writes to `registros/gui_state.json`; in multi-machine or Docker setups it pushes via HTTP POST to the telemetry container, which exposes an HTTP endpoint on port 8080 and publishes events to RabbitMQ.

### Audio Follows Video
When the operator switches the program source, the audio mix follows automatically: the outgoing source fades out and the incoming source fades in — no manual intervention on the audio toolbar required.

### Auto-Off Overlays
Overlays and dynamic titles are automatically dismissed on every cut or composite change, preventing stale on-air graphics from carrying over to the next segment.

### Docker Containerization
The full production stack — core, sources, stream blanker, telemetry, audio manager and RabbitMQ broker — runs as a single `docker compose up` command. Health checks enforce correct startup order; camera containers share the voctocore network namespace so they communicate over localhost without virtual network overhead.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       voctogui (GTK)                        │
│   Sources A/B · Composites · Blanker · Overlays · Titling   │
└──────────────────────────┬──────────────────────────────────┘
                           │  TCP :9999 (control)
                           │  TCP :14000-14005 (source previews)
┌──────────────────────────▼──────────────────────────────────┐
│                  voctocore  (Python + GStreamer)             │
│                                                             │
│   cam1   :10000 ─┐                                          │
│   cam2   :10001 ─┤                                          │
│   cam3   :10002 ─┼──► compositor ──► stream-blanker ───────►│ :15000  program out
│   cam4   :10003 ─┤                 └───────────────────────►│ :11000  raw mix
│   break  :10004 ─┤                                          │
│   intro  :10005 ──┘                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │       Telemetry / RabbitMQ       │
          │   HTTP :8080  ·  AMQP :5672      │
          └──────────────────────────────────┘
```

**voctocore** accepts incoming A/V streams over TCP (Matroska container, UYVY + PCM S16LE), mixes them via GStreamer's `compositor` element, and exposes the program output on port 15000. It is controlled by a text-command TCP interface on port 9999.

**voctogui** is a GTK client that connects to voctocore, displays live previews of all sources and the mix, and provides the full operator toolbar.

---

## Prerequisites

### Native (Scenarios 1 & 2)

- **OS:** Ubuntu 22.04 LTS or Debian Bookworm
- **Python:** 3.10+
- **GStreamer:** 1.20+ recommended

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

- **Docker:** 24.0+
- **Docker Compose plugin:** v2.20+ (`docker compose`, not `docker-compose`)
- A working **X11 display** on the host (voctogui runs natively, not in a container)

```bash
docker compose version   # verify installation
```

---

## Quick Start

```bash
git clone https://github.com/<your-username>/voctomix2.0.git
cd voctomix2.0
```

> Place your VTR assets in `videos/` before launching:
> `videos/intro.mp4`, `videos/SLIDES_video_starting_soon.mp4`,
> `videos/stream_offline.mp4`, `videos/musica_pausa.mp3`

---

### Scenario 1 — Single PC (native)

Runs voctocore, all test sources, telemetry, a PROGRAM monitor and voctogui on one machine.

```bash
./start_studio_single_pc.sh
```

The script auto-detects your LAN IP, cleans up any previous processes, waits for port 9999 to be listening, then opens the GUI. Closing the GUI window shuts everything down cleanly.

The self-contained configuration for this scenario is also available in `1pc_escenario1/`:

```bash
cd 1pc_escenario1/ && ./start_studio_single_pc.sh
```

---

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

Both machines must be on the same LAN with the ports in the [Port Reference](#port-reference) table reachable between them.

---

### Scenario 3 — Docker (recommended)

The most reproducible deployment. One script builds the image, starts all 10 services in order, waits for health checks to pass, then opens voctogui on the host.

```bash
# Allow the host GUI to receive the voctogui window
xhost +local:$(id -un)

./launch_docker_studio.sh
```

To override the LAN IP used by the telemetry service:

```bash
MI_IP_REAL=10.0.0.5 ./launch_docker_studio.sh
```

**Stop the stack:**

```bash
sudo docker compose down
```

**Services started by `docker compose up`:**

| Container | Role | Exposed ports |
|---|---|---|
| `voctocore` | GStreamer mixer core | 9999, 9998/udp, 10000–10005, 11000, 12000, 13000–13005, 14000–14005, 15000 |
| `rabbitmq` | AMQP message broker | 5672, 15672 (web UI) |
| `telemetry` | GUI state HTTP endpoint + RabbitMQ publisher | 8080 |
| `cam1`–`cam4` | Synthetic test video sources | — (internal, share voctocore network) |
| `break` | Break/pause video source | — |
| `intro` | Intro video loop (port 10005) | — |
| `stream_blanker` | Blanker video source | — |
| `audio_manager` | Dynamic audio controller | — |

---

### Scenario 4 — Kubernetes

Orchestrated deployment on a local Minikube cluster, mirroring the two-PC roles at the orchestration level.

```bash
# PC 1 (server): starts Minikube, applies manifests, opens port-forward
./k8s_escenario/start_server_pc1.sh

# PC 2 (operator): runs voctogui against the forwarded address
./k8s_escenario/start_operator_pc2.sh
```

All containers in the `studio` Pod share one network namespace (same loopback pattern as Docker Compose). RabbitMQ runs as a StatefulSet with a PersistentVolumeClaim for queue durability. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the full walkthrough.

---

## Documentation

In-depth documentation lives in [`docs/`](docs/):

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
voctomix2.0/
│
├── voctocore/                      # GStreamer mixer server (Python)
│   ├── voctocore.py                # Entry point
│   ├── default-config.ini          # Mix configuration (sources, caps, blanker…)
│   └── lib/
│       ├── streamblanker.py        # [NEW] LIVE/PAUSE/NOSTREAM pipeline
│       ├── audiomix.py             # [NEW] Audio-Follows-Video logic
│       ├── videomix.py             # GStreamer compositor
│       ├── overlay.py              # Overlay image injection
│       ├── composites.py           # Composite definitions (fs, pip, sbs, lecture…)
│       └── controlserver.py        # TCP control protocol (:9999)
│
├── voctogui/                       # GTK operator interface (Python)
│   ├── voctogui.py                 # Entry point
│   ├── default-config.ini          # GUI configuration
│   └── lib/
│       ├── gui_state_exporter.py   # [NEW] Telemetry JSON exporter
│       └── toolbar/
│           ├── streamblank.py      # [NEW] Stream status toolbar
│           └── overlay.py          # [NEW] Dynamic titling + auto-off
│
├── example-scripts/ffmpeg/         # Source injection and utility scripts
│   ├── source-testvideo-as-cam*.sh # Synthetic cameras via FFmpeg
│   ├── stream_blanker_source.sh    # Blanker source
│   ├── auto_launch_intro.sh        # Intro VTR watchdog
│   ├── stream-hd-to-youtube.sh     # H.264 stream to YouTube Live
│   ├── record-mixed-ffmpeg.sh      # Program recording
│   ├── telemetry_service.py        # [NEW] HTTP + RabbitMQ telemetry backend
│   └── audio_control.sh            # [NEW] Dynamic audio controller
│
├── 1pc_escenario1/                 # Scenario 1: single-PC scripts
├── 2pc_escenario2/                 # Scenario 2: server + operator scripts
├── docker_escenario3/              # Scenario 3: Docker variant scripts
│
├── images/                         # Overlay graphics and backgrounds
├── videos/                         # VTR assets (add your own; see Quick Start)
├── registros/                      # Telemetry output (auto-created at runtime)
│
├── Dockerfile                      # Ubuntu 22.04 + GStreamer + FFmpeg + pika
├── docker-compose.yml              # 10-service production stack
├── launch_docker_studio.sh         # [Scenario 3] One-command Docker launcher
├── start_studio_single_pc.sh       # [Scenario 1] Single-PC native launcher
├── start_server.sh                 # [Scenario 2] Server-only launcher
├── .env.example                    # Environment variable template (copy to .env)
├── .github/workflows/              # CI: tests, lint, Docker build on push
├── docs/                           # Project documentation (architecture, API, deployment)
├── .claude/                        # Claude Code context (rules, memory, templates)
└── memoria_tfg/                    # LaTeX source of the Bachelor's Thesis
```

---

## Port Reference

| Port | Protocol | Direction | Description |
|------|----------|-----------|-------------|
| 9999 | TCP | → voctocore | Control protocol (text commands) |
| 9998 | UDP | broadcast | GStreamer `GstNetTimeProvider` (A/V sync clock) |
| 10000–10003 | TCP | → voctocore | Camera inputs cam1–cam4 (MKV/UYVY+S16LE) |
| 10004 | TCP | → voctocore | Break / pause source |
| 10005 | TCP | → voctocore | Intro video source |
| 11000 | TCP | ← voctocore | Raw program mix (MKV/UYVY+S16LE) |
| 12000 | TCP | ← voctocore | Mix preview (JPEG/MKV) |
| 13000–13005 | TCP | ← voctocore | Per-source recording outputs |
| 14000–14005 | TCP | ← voctocore | Per-source preview outputs (GUI) |
| 15000 | TCP | ← voctocore | Post-blanker program output (stream feed) |
| 8080 | HTTP | ← telemetry | GUI state JSON endpoint |
| 5672 | AMQP | ↔ RabbitMQ | Message broker |
| 15672 | HTTP | ← RabbitMQ | RabbitMQ management web UI |

---

## Configuration

voctocore is configured via `voctocore/default-config.ini`. Key sections:

```ini
[mix]
sources = cam1,cam2,cam3,cam4,break,intro
videocaps = video/x-raw,format=UYVY,width=1920,height=1080,framerate=25/1
audiocaps = audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000

[stream-blanker]
enabled = true
sources = pause,nostream   # Drives the PAUSE and NOSTREAM buttons in the GUI
volume = 1.0

[overlay]
path = ./images
auto-off = true
blend-time = 300           # ms for overlay fade in/out

[previews]
enabled = true
videocaps = video/x-raw,width=1024,height=576,framerate=25/1

[mirrors]
enabled = true
```

Any value defined in the core configuration automatically overrides the GUI's equivalent, keeping all connected GUI instances in sync.

---

## Telemetry JSON format

Every second, `GuiStateExporter` publishes a full snapshot of the mixer state. Example:

```json
{
  "last_update": "2026-04-22 14:35:01",
  "gui_ip": "192.168.1.10",
  "preview": {
    "channel_a": "cam1",
    "channel_b": "cam2"
  },
  "mode": "live",
  "composite": {
    "name": "full_screen",
    "fullscreen": true,
    "side_by_side": false,
    "pip": false,
    "lecture": false
  },
  "mirror": false,
  "insertion": {
    "overlay": false,
    "auto_off": true,
    "overlay_selected": "logo_event.png",
    "text1_active": true,
    "text1_value": "Speaker Name — TFG 2026",
    "text2_active": false,
    "text2_value": ""
  },
  "audio": {
    "cam1_db": -18.5,
    "cam2_db": -42.0,
    "cam3_db": null,
    "cam4_db": null,
    "break_db": null,
    "intro_db": null
  }
}
```

**Docker / network mode:** available at `http://localhost:8080/gui_state`  
**Native mode:** written to `registros/gui_state.json`

---

## Based On

This project is a fork and extension of [voc/voctomix](https://github.com/voc/voctomix) (branch `voctomix2`), originally developed by the C3VOC team. New features, Docker containerization, launch scripts and this documentation were developed as part of a Bachelor's Thesis in Telecommunication Engineering, 2025–2026.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the
development setup, coding conventions (clean, modular, English-only code and
comments), commit-message rules (Conventional Commits) and the test/lint flow.

Before opening a pull request:

```bash
make test    # voctocore unit tests (mock GI bindings, no display needed)
make lint    # pycodestyle
```

## Support

- 🐛 Found a bug or have a question? Open an [issue](../../issues).
- 🔧 Stuck on setup? See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## License

[MIT](LICENSE.txt)
