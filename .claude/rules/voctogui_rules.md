# voctogui Rules

Rules for editing code under `voctogui/`.

---

## Architecture

- voctogui is a pure GTK 3 client. It never touches GStreamer directly — all mixer control goes through the TCP socket at port 9999.
- `voctogui/voctogui.py` is the entry point. It instantiates the main window and starts the asyncio event loop alongside GTK's main loop.
- The connection to voctocore is managed by `lib/connection.py`. All command sends and response callbacks go through it.

## GUI Structure

```
voctogui/lib/
├── toolbar/          ← Action widgets (source buttons, composite selector, stream blanker, overlay)
│   ├── streamblank.py    LIVE / PAUSE / NOSTREAM buttons
│   ├── overlay.py        lower-thirds + auto-off on cut
│   └── ...
├── videodisplay/     ← Preview widgets (GStreamer sinks embedded in GTK)
├── connection.py     ← Async TCP client, message dispatcher
├── uibuilder.py      ← Loads .ui Glade files
└── gui_state_exporter.py  ← Telemetry: JSON every 1s
```

## Communication Pattern

- Sending a command: `Connection.send('set_video_a cam1')` — fire and forget.
- Receiving responses: register a callback with `Connection.on('video_status', handler)`. The dispatcher calls all registered handlers on matching event name.
- Never block the GTK main loop waiting for a response. Use async callbacks.

## Telemetry Exporter (gui_state_exporter.py)

- Walks the live GUI widget tree to capture current state (active source, composite mode, blanker state, overlay text, audio levels).
- In native mode: writes `registros/gui_state.json` (JSON Lines format, one object per line).
- In Docker mode: HTTP POST to `http://localhost:8080` (telemetry service).
- Runs on a 1-second timer via `GLib.timeout_add(1000, ...)`. Must not block.
- Never use the word "Notario" anywhere in this module or its comments.

## CSS / Theming

- Dark theme CSS is at `voctogui/ui/style.css`.
- Custom widget colors use GTK CSS class selectors (`.source-active`, `.blanker-live`, etc.).
- SVG icons in `voctogui/ui/icons/`. Prefer SVG over PNG for resolution independence.

## Auto-Off on Cut

- When `set_composite_mode` or `set_video_*` is sent, the overlay toolbar automatically calls `show_overlay false` via the connection.
- This logic lives in `lib/toolbar/overlay.py`. Do not duplicate it in other toolbar widgets.

## Style Rules

- All widget labels in English (internal) or Spanish (displayed to operator) — check existing labels before adding new ones.
- GTK signals use underscore naming: `on_button_clicked`, `on_scale_value_changed`.
- Never import from `voctocore/` — maintain strict client/server separation.
