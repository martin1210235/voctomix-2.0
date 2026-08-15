# Control Protocol (TCP :9999)

All mixer control is carried over a **line-delimited ASCII protocol** on TCP
port 9999, implemented in `voctocore/lib/commands.py` and `controlserver.py`.

This machine-readable API is a core differentiator of Voctomix: any scripted
client — a cron job, a web backend, an automation system — can control the mixer
with a single TCP socket and standard line I/O.

## Protocol semantics

- Each command is a single UTF-8 line terminated by a newline (`\n`).
- The server validates the command, executes the pipeline action, and
  **broadcasts** a response event of the same form to **all** connected clients,
  so multiple `voctogui` instances stay consistent without a separate sync
  mechanism.
- A command with invalid arguments returns an `error` event to the originating
  client only.
- `get_*` commands return the current value; `set_*`/`show_*` mutate state.

### Quick try

```bash
# Switch channel A to cam2 and read it back
printf 'set_video_a cam2\nget_video\n' | nc 127.0.0.1 9999
```

## Command reference

Grounded in `voctocore/lib/commands.py`.

### Video sources and composite

| Command | Args | Effect |
|---|---|---|
| `get_video` | — | Current A/B source assignment |
| `set_video_a` | `<source>` | Assign a source slot to channel A |
| `set_video_b` | `<source>` | Assign a source slot to channel B |
| `get_composite_mode` | — | Current composite mode |
| `get_composite_modes` | — | Legacy mode-list query |
| `set_composite_mode` | `<mode>` | Change the layout using a configured composite identifier |
| `set_videos_and_composite` | `<src_a> <src_b> <mode>` | Set A, B and mode atomically |
| `get_composite` | — | Full composite state |
| `transition` | `<command>` | Animated transition to a new state |
| `cut` | `<command>` | Hard cut to a new state |

`<source>` ∈ `cam1..cam4`, `break`, `intro`. The shipped configuration uses the
composite identifiers `fs`, `sbs`, `pip`, `lec` and `lec_43`, plus mirrored
variants with the `|` prefix where configured. The `cut` and `transition`
commands accept the composite-command form used internally by voctogui, for
example `cut fs(cam1,*)` or `transition sbs(cam1,cam2)`.

### Audio

| Command | Args | Effect |
|---|---|---|
| `get_audio` | — | Current audio source/levels |
| `set_audio` | `<source>` | Select the active audio source |
| `set_audio_volume` | `<source> <volume>` | Set per-source volume |

Audio Follows Video automatically tracks channel A; manual overrides re-engage
AFV on the next switch.

### Stream blanker (output gating)

| Command | Args | Effect |
|---|---|---|
| `get_stream_status` | — | Current blanker state |
| `set_stream_blank` | `<source>` | Gate output (e.g. `pause`, `nostream`) |
| `set_stream_live` | — | Return output to LIVE |

### Overlay and titling

| Command | Args | Effect |
|---|---|---|
| `set_overlay` | `<overlay>` | Select the overlay graphic |
| `show_overlay` | `<true\|false>` | Activate/deactivate (500 ms fade) |
| `get_overlay` / `get_overlay_visible` | — | Current overlay / visibility |
| `get_overlays` / `get_overlays_title` | — | Available overlays / titles |
| `show_logo1` / `show_logo2` | `<true\|false>` | Toggle logo layers |
| `set_text` | `<...>` | Set text layer 1 |
| `set_text2` | `<...>` | Set text layer 2 |

The overlay is auto-deactivated on every cut: `voctogui` sends
`show_overlay false` before forwarding a source/composite change.

### Configuration and source management

| Command | Args | Effect |
|---|---|---|
| `get_config` | — | Full effective configuration |
| `get_config_option` | `<section> <key>` | A single config value |
| `get_sources_status` | — | Connection status of all sources |
| `restart_source` | `<source>` | Restart a source ingest |
| `help` | — | List available commands |

> The core configuration overrides the GUI's equivalent values, keeping all
> connected GUI instances in sync. See [CONFIGURATION.md](CONFIGURATION.md).
