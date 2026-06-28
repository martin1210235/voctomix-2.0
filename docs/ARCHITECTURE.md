# Architecture

Voctomix 2.0 follows a strict **client–server** separation inherited from the
original C3VOC design and extended with containerization and telemetry.

- **voctocore** — the processing server. Hosts a single GStreamer pipeline that
  ingests up to six A/V streams over TCP, performs compositing, audio mixing,
  overlay injection and output gating, and delivers the program signal.
- **voctogui** — the operator interface. A GTK 3 desktop application that
  controls the core over a line-based TCP protocol and renders live previews.

Multiple `voctogui` instances may connect to one `voctocore` simultaneously,
enabling multi-operator workflows without restarting the engine.

```
┌─────────────────────────────────────────────────────────────┐
│                       voctogui (GTK 3)                       │
│   Sources A/B · Composites · Blanker · Overlays · Titling    │
└──────────────────────────┬──────────────────────────────────┘
                           │  TCP :9999 (control)
                           │  TCP :14000-14005 (source previews)
┌──────────────────────────▼──────────────────────────────────┐
│                  voctocore  (Python + GStreamer)             │
│   cam1 :10000 ─┐                                             │
│   cam2 :10001 ─┤                                             │
│   cam3 :10002 ─┼─► compositor ─► audiomix ─► overlay ─►      │
│   cam4 :10003 ─┤                          stream-blanker ─►  │ :15000 program
│   break :10004 ┤                                             │ :11000 raw mix
│   intro :10005 ┘                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │       Telemetry / RabbitMQ       │
          │   HTTP :8080  ·  AMQP :5672      │
          └──────────────────────────────────┘
```

## voctocore — the processing core

### GStreamer pipeline

`pipeline.py` builds a single static pipeline at startup. The internal format is
**I420 (YUV 4:2:0)** at 1920×1080 px, 25 fps; audio is **S16LE** PCM at 48 kHz,
stereo. Formats are negotiated once at source boundaries via GStreamer caps and
kept throughout the pipeline without intermediate re-encoding.

> Source of truth for caps: `voctocore/default-config.ini`.

Inter-module data flow uses `appsrc`/`appsink` pairs so each module
(`videomix.py`, `audiomix.py`, `overlay.py`, `streamblanker.py`) is an
independent Python object. All GStreamer state transitions are confined to
initialization; the graph is static during operation.

A `NetTimeProvider` broadcasts a GStreamer network clock over UDP 9998; all
camera-ingest processes synchronize to it for presentation-time alignment.

### Source management

Six logical slots: `cam1`–`cam4` (live), `break` (interstitial loop), `intro`
(opening). Each listens on a dedicated TCP port (10000–10005). The source plugin
is selected per slot via `kind=` in the config:

| Plugin | File | Use |
|---|---|---|
| TCP A/V source | `lib/sources/tcpavsource.py` | Matroska-over-TCP from an upstream FFmpeg process |
| Image source | `lib/sources/imgvsource.py` | Static PNG/JPEG loop (break, intro in native) |
| DeckLink source | `lib/sources/decklinkavsource.py` | Hardware SDI capture card |

### Compositing — `videomix.py` + `composites.py`

Two logical channels A and B, each assigned to a source slot. On a switch, the
GStreamer `compositor` pad offsets/dimensions/alpha are updated per the active
composite mode; the change takes effect at the next buffer boundary (clean cut).

Modes: Fullscreen A/B, Picture-in-Picture, Side-by-Side Equal, Side-by-Side
Preview, Lecture, Lecture 4:3.

### Audio Follows Video — `audiomix.py`

On a source-A change, the module cross-fades the outgoing and incoming audio
channels by interpolating the GStreamer `volume` property over a configurable
duration (default 200 ms). Independent of composite mode; operators may override
manually and AFV re-engages on the next switch.

### Stream blanker — `streamblanker.py`

A GStreamer `input-selector` chooses among three output paths to port 15000,
independently of the internal mix:

- **LIVE** — mixed program passes through.
- **PAUSE** — a dedicated pause source (static loop, port 17000) with background
  audio (port 18000); the internal mix keeps evolving off-air.
- **NOSTREAM** — silent black frame; output cut entirely.

### Overlay — `overlay.py`

A `gdkpixbufoverlay` element for PNG lower-thirds plus two independent
`textoverlay` elements. Fade in/out animates the `alpha` property over 500 ms.
The overlay is auto-deactivated on every cut: `voctogui` issues `show_overlay
false` before forwarding a source/composite change.

## voctogui — the control interface

A GTK 3 application running an asyncio loop alongside the GTK main loop with
non-blocking TCP I/O. Three panels: source previews (JPEG, ports 14000–14005),
program monitor, and the central toolbar (A/B selectors, composite drop-down,
LIVE/PAUSE/NOSTREAM, overlay controls).

`gui_state_exporter.py` runs a 1 s timer capturing the full mixer state as JSON.
See [TELEMETRY.md](TELEMETRY.md).

## Shared library — `vocto/`

`vocto/composite_commands.py` defines the composite-mode enum shared by both
components. Import from here; do not duplicate in either side.

## Further reading

- Control protocol → [CONTROL_PROTOCOL.md](CONTROL_PROTOCOL.md)
- Telemetry chain → [TELEMETRY.md](TELEMETRY.md)
- Deployment scenarios → [DEPLOYMENT.md](DEPLOYMENT.md)
