# Configuration Reference

`voctocore` is configured through `voctocore/default-config.ini`. Any value set
in the core configuration overrides the GUI's equivalent, so every connected
`voctogui` instance stays in sync automatically.

> The values below reflect the shipped `default-config.ini`. This is a
> reference document — for *why* the pipeline is built this way, see
> [ARCHITECTURE.md](ARCHITECTURE.md).

## `[mix]` — core format and sources

```ini
[mix]
videocaps = video/x-raw,format=I420,width=1920,height=1080,framerate=25/1,pixel-aspect-ratio=1/1,interlace-mode=progressive,colorimetry=bt709
audiocaps = audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000
sources = cam1,cam2,cam3,cam4,break,intro
backgrounds = background1,background2
audiostreams = 1
```

| Key | Meaning |
|---|---|
| `videocaps` | Internal video format. **I420 (YUV 4:2:0)**, 1920×1080, 25 fps |
| `audiocaps` | Internal audio format. S16LE, 48 kHz, stereo |
| `sources` | Logical source slots (drive the A/B selector buttons) |
| `backgrounds` | Background sources for composite modes |
| `audiostreams` | Number of audio streams per source |

## `[source.*]` — per-source options

Each slot (`cam1`–`cam4`, `break`, `intro`, blanker sources) has its own
section. The source plugin is chosen with `kind=` (e.g. `tcp`, `img`,
`decklink`); `deinterlace = assume-progressive` is set on the camera slots.

## `[stream-blanker]` — output gating

```ini
[stream-blanker]
enabled = true
sources = pause,nostream    # drive the PAUSE and NOSTREAM buttons in the GUI
volume = 1.0
```

The `[source.stream-blanker-pause]` and `[source.stream-blanker-nostream]`
sections define the PAUSE slate and the NOSTREAM black/silence source.

## `[overlay]` — lower-thirds and titling

```ini
[overlay]
path = ./images
auto-off = true
blend-time = 300            # ms for overlay fade in/out
```

| Key | Meaning |
|---|---|
| `path` | Directory of overlay PNG graphics |
| `auto-off` | Dismiss the overlay automatically on every cut |
| `blend-time` | Fade duration in milliseconds |

`[logo1]` and `[logo2]` configure independent logo layers.

## `[previews]` and `[mirrors]`

```ini
[previews]
enabled = true
videocaps = video/x-raw,width=1024,height=576,framerate=25/1

[mirrors]
enabled = true
```

Preview streams (ports 14000–14005) are downscaled to 1024×576 to reduce GUI
bandwidth; `[mirrors]` exposes per-source mirror outputs.

## `[output-buffers]`, `[composites]`, `[transitions]`

- `[output-buffers]` tunes the output queue depth.
- `[composites]` defines the geometry of each composite mode (fullscreen, PIP,
  side-by-side, lecture and variants).
- `[transitions]` defines the animated transitions between composite modes.

## GUI configuration

`voctogui/default-config.ini` holds GUI-only layout options. Remember: any key
also present in the core config is overridden by the core to keep all GUIs
consistent.
