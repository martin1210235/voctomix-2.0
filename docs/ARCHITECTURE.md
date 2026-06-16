# Voctomix 2.0 — Architecture Reference

Deep-dive architecture document. For quick overview see [.claude/MEMORY.md](../.claude/MEMORY.md).

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        HOST MACHINE                              │
│                                                                  │
│   ┌─────────────┐   TCP :9999 (control)   ┌──────────────────┐  │
│   │  voctogui   │ ─────────────────────── │   voctocore      │  │
│   │  (GTK 3)    │ ─── TCP :14000-14005 ── │  (GStreamer)     │  │
│   └─────────────┘     source previews     └──────┬───────────┘  │
│                                                  │              │
│   ┌─────────────┐                         ┌──────▼───────────┐  │
│   │  telemetry  │ ─── HTTP :8080 ──────── │  gui_state_exp.  │  │
│   │  service    │ ─── AMQP :5672 ─────┐  └──────────────────┘  │
│   └─────────────┘                     │                         │
│   ┌─────────────┐                     │  ┌──────────────────┐   │
│   │  RabbitMQ   │ ◄───────────────────┘  │  cam1-4 / break  │   │
│   │  :5672      │                        │  / intro / audio  │   │
│   └─────────────┘                        └──────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## voctocore GStreamer Pipeline

### Input Sources

Each source connects over TCP. voctocore listens on each port and accepts a Matroska stream (video + audio muxed):

```
cam1 (TCP :10000) ──┐
cam2 (TCP :10001) ──┤
cam3 (TCP :10002) ──┤──► videomix (compositor) ──► streamblanker ──► :15000 (program out)
cam4 (TCP :10003) ──┤         │                         │
break (TCP :10004) ─┤         ▼                         ▼
intro (TCP :10005) ─┘    overlay (PNG/text)        :11000 (raw mix)
```

### Video Pipeline Detail

```
tcpserversrc port=10000
  └─► matroskademux
        ├─► video: videoconvert ──► videoscale ──► capsfilter(UYVY 1920x1080 25fps)
        │         └─► input_selector[cam1]
        └─► audio: audioconvert ──► audioresample ──► capsfilter(S16LE 48kHz stereo)
                  └─► audiomixer[cam1]

[all sources] ──► videomixer ──► overlay_bin ──► tee
                                                  ├─► :11000 (raw mix, matroskamux)
                                                  ├─► :12000 (JPEG preview, jpegenc)
                                                  └─► streamblanker ──► :15000 (program)
```

### Audio Pipeline Detail

```
audiomixer (N inputs, one per source)
  └─► volume(source-level faders)
       └─► audiomixer (master)
            └─► tee ──► :11000 (raw mix)
                    └─► :15000 (program, post-blanker)
```

Audio Follows Video: when `set_video_a src` is called, `audiomix.py` fades out the old source volume and fades in the new one over 100ms.

### Compositor Modes

Implemented in `voctocore/lib/composites.py` as `Composite` dataclasses:

| Mode | A position | B position |
|------|-----------|-----------|
| `fullscreen` | 1920×1080 @ (0,0) | hidden |
| `side_by_side_equal` | 960×1080 @ (0,0) | 960×1080 @ (960,0) |
| `side_by_side_preview` | 1280×1080 @ (0,0) | 640×1080 @ (1280,0) |
| `picture_in_picture` | 1920×1080 @ (0,0) | 320×240 @ (1600,840) |
| `lecture` | 1280×1080 @ (0,0) | 640×1080 @ (1280,0) |
| `lecture_4:3` | 1440×1080 @ (0,0) | 480×1080 @ (1440,0) — crop 31% |

### Stream Blanker States

```
                    ┌── LIVE ──────► :15000 = program mix
voctocore output ───┤
                    ├── PAUSE ─────► :15000 = :17000 (PAUSE video, no audio)
                    │
                    └── NOSTREAM ──► :15000 = :17001 (OFFLINE video, no audio)
```

The blanker inserts a `funnel` element that selects between the program mix and the two blanker sources.

---

## voctogui Architecture

```
voctogui.py (entry point)
  ├── asyncio event loop (co-runs with GLib main loop)
  ├── connection.py
  │     ├── asyncio TCP client → voctocore :9999
  │     ├── send(command_string)
  │     └── on(event_name, callback) [event dispatcher]
  ├── uibuilder.py → loads .ui Glade XML files
  ├── toolbar/
  │     ├── sources.py → source A/B selector buttons
  │     ├── composites.py → composite mode buttons
  │     ├── streamblank.py → LIVE/PAUSE/NOSTREAM
  │     └── overlay.py → lower-thirds + auto-off logic
  ├── videodisplay/
  │     └── previews.py → 6 GStreamer sinks (source previews, mix preview)
  └── gui_state_exporter.py → 1Hz JSON telemetry
```

### TCP Protocol Flow

```
voctogui                              voctocore
   │─── "set_video_a cam1\n" ────────────►│
   │◄── "video_status cam1 cam2\n" ────────│  (NotifyResponse → all clients)
   │◄── "video_status cam1 cam2\n" ────────│  (broadcast to all connected GUIs)
```

---

## Docker Network Architecture

```
                  voctomix_net (bridge)
                  ┌───────────────────────────────────┐
                  │  voctocore  ◄──── telemetry        │
                  │  rabbitmq   ◄──── telemetry        │
                  └───────────────────────────────────┘

  network_mode: service:voctocore  (shared network namespace)
  ┌────────────────────────────────────────────────────────────┐
  │  cam1 / cam2 / cam3 / cam4 / break / intro                 │
  │  stream_blanker / audio_manager                            │
  │  → communicate with voctocore via 127.0.0.1:PORT           │
  └────────────────────────────────────────────────────────────┘
```

The shared network namespace eliminates virtual network overhead for camera streams — cameras connect to voctocore as if running on the same process.

---

## Telemetry Data Flow

```
voctogui (gui_state_exporter.py, 1Hz)
  ├── Native: write → registros/gui_state.json (JSON Lines)
  └── Docker: HTTP POST → telemetry service :8080
                              ├── store JSON locally
                              └── publish → RabbitMQ exchange (AMQP)
                                              └── consumers (analytics, monitoring)
```

### JSON State Schema

```json
{
  "timestamp": "2026-05-13T10:30:00.000Z",
  "video_a": "cam1",
  "video_b": "cam2",
  "composite_mode": "side_by_side_equal",
  "stream_status": "live",
  "overlay_visible": false,
  "overlay_text": "",
  "audio_volumes": {
    "cam1": 1.0, "cam2": 0.0, "cam3": 0.0, "cam4": 0.0
  }
}
```

---

## Configuration Files

### voctocore/default-config.ini (key sections)

```ini
[mix]
sources = cam1, cam2, cam3, cam4
videocaps = video/x-raw,format=UYVY,width=1920,height=1080,framerate=25/1
audiocaps = audio/x-raw,format=S16LE,rate=48000,channels=2

[stream-blanker]
enabled = true
sources = pause, offline

[overlay]
files = logo.png, banner.png
```

### Port Summary

| Port | Direction | Protocol | Service |
|------|-----------|----------|---------|
| 9999 | IN | TCP | Control commands |
| 9998 | IN/OUT | UDP | GStreamer clock sync |
| 10000-10003 | IN | TCP (Matroska) | cam1-cam4 |
| 10004 | IN | TCP (Matroska) | break source |
| 10005 | IN | TCP (Matroska) | intro source |
| 11000 | OUT | TCP (Matroska) | raw mix output |
| 12000 | OUT | TCP (JPEG) | mix preview |
| 13000-13005 | OUT | TCP (Matroska) | per-source mirrors |
| 14000-14005 | OUT | TCP (JPEG) | per-source previews (GUI) |
| 15000 | OUT | TCP (Matroska) | program output (post-blanker) |
| 17000 | IN | TCP (Matroska) | PAUSE video source |
| 17001 | IN | TCP (Matroska) | NOSTREAM video source |
| 18000 | IN | TCP (Matroska) | background audio |
| 8080 | IN | HTTP | Telemetry REST API |
| 5672 | IN/OUT | AMQP | RabbitMQ messaging |
| 15672 | OUT | HTTP | RabbitMQ web UI |
