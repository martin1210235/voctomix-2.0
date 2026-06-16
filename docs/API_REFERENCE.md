# voctocore TCP Control Protocol — API Reference

Port: **9999 TCP**, line-based text protocol.

## Protocol Format

```
REQUEST:  <command_name> [arg1] [arg2] ...\n
RESPONSE: ok <event_name> [data]\n          (OkResponse — only to sender)
          notify <event_name> [data]\n       (NotifyResponse — broadcast to ALL clients)
          error <message>\n                  (on exception)
```

Arguments with spaces must be URL-encoded (`urllib.parse.quote`). The server automatically URL-decodes received arguments.

---

## Video Commands

### `get_video`
Get current video source A and source B.
```
→ get_video
← ok video_status cam1 cam2
```

### `set_video_a <source>`
Set video source A. If `<source>` is currently B, they are swapped.
```
→ set_video_a cam2
← notify video_status cam2 cam1   (broadcast)
```

### `set_video_b <source>`
Set video source B. If `<source>` is currently A, they are swapped.
```
→ set_video_b cam3
← notify video_status cam1 cam3
```

**Valid source names:** `cam1`, `cam2`, `cam3`, `cam4`, `break`, `intro` (configured in `default-config.ini → [mix] sources`).

---

## Composite Mode Commands

### `get_composite_mode`
Get current compositor mode.
```
→ get_composite_mode
← ok composite_mode side_by_side_equal
```

### `set_composite_mode <mode>`
Set compositor mode.
```
→ set_composite_mode picture_in_picture
← notify composite_mode picture_in_picture
← notify video_status cam1 cam2
← notify composite_mode_and_video_status picture_in_picture cam1 cam2
```

**Valid modes:** `fullscreen`, `side_by_side_equal`, `side_by_side_preview`, `picture_in_picture`, `lecture`, `lecture_4:3`

### `get_composite_mode_and_video_status`
Get both composite mode and video sources in one call (atomic read).
```
→ get_composite_mode_and_video_status
← ok composite_mode_and_video_status side_by_side_equal cam1 cam2
```

### `set_videos_and_composite <src_a> <src_b> <mode>`
Atomically set A source, B source, and composite mode.
```
→ set_videos_and_composite cam1 cam2 side_by_side_equal
← notify composite_mode side_by_side_equal
← notify video_status cam1 cam2
← notify composite_mode_and_video_status side_by_side_equal cam1 cam2
```

### `get_composite`
Get current composite in composite command format (`mode/src_a/src_b`).
```
→ get_composite
← ok composite side_by_side_equal/cam1/cam2
```

### `transition <composite_command>`
Apply composite change with transition (animated).
```
→ transition side_by_side_equal/cam1/cam2
← notify composite side_by_side_equal/cam1/cam2
```

### `cut <composite_command>`
Apply composite change as a hard cut (no transition).
```
→ cut fullscreen/cam1/*
← notify composite fullscreen/cam1/cam2
```

---

## Audio Commands

### `get_audio`
Get current volume for all sources (JSON).
```
→ get_audio
← ok audio_status {"cam1": 1.0, "cam2": 0.0, "cam3": 0.0, "cam4": 0.0}
```

### `set_audio <source>`
Set active audio source (Audio Follows Video trigger — applies fade).
```
→ set_audio cam2
← notify audio_status {"cam1": 0.0, "cam2": 1.0, "cam3": 0.0, "cam4": 0.0}
```

### `set_audio_volume <source> <float>`
Set volume for a specific source. Range: `0.0` (mute) to `1.0` (full).
```
→ set_audio_volume cam1 0.5
← notify audio_status {"cam1": 0.5, "cam2": 0.5, "cam3": 0.0, "cam4": 0.0}
```

---

## Stream Blanker Commands

Available only when `stream-blanker` is enabled in config.

### `get_stream_status`
Get current stream blanker state.
```
→ get_stream_status
← ok stream_status live
← ok stream_status blank pause    (when blanked to PAUSE source)
```

### `set_stream_blank <blanker_source>`
Activate stream blanker with the specified source.
```
→ set_stream_blank pause
← notify stream_status blank pause

→ set_stream_blank offline
← notify stream_status blank offline
```

**Valid blanker sources:** `pause`, `offline` (configured in `default-config.ini → [stream-blanker] sources`).

### `set_stream_live`
Deactivate blanker and restore live program.
```
→ set_stream_live
← notify stream_status live
```

---

## Overlay Commands

Available only when overlay is configured in `default-config.ini`.

### `get_overlays`
List available overlay files (URL-encoded filenames).
```
→ get_overlays
← notify overlays logo.png,banner.png
```

### `get_overlays_title`
List available overlay display names.
```
→ get_overlays_title
← notify overlays_title Logo,Banner
```

### `set_overlay <overlay_name>`
Load and activate an overlay by filename.
```
→ set_overlay logo.png
← notify overlay logo.png
```

### `show_overlay <true|false>`
Show or hide the current overlay.
```
→ show_overlay true
← notify overlay_visible True

→ show_overlay false
← notify overlay_visible False
```

### `get_overlay`
Get current overlay filename.

### `get_overlay_visible`
Get overlay visibility state.

---

## Dynamic Text Overlay Commands

### `set_text <text>`
Set dynamic text overlay line 1. URL-encode spaces and special characters.
```
→ set_text Martin%20García%20-%20Ponente
← notify text_updated Martin%20García%20-%20Ponente
```

### `set_text2 <text>`
Set dynamic text overlay line 2.
```
→ set_text2 Universidad%20Politécnica%20de%20Madrid
← notify text2_updated Universidad%20Politécnica%20de%20Madrid
```

---

## Logo Commands

Available only when logo1/logo2 are configured.

### `show_logo1 <true|false>`
### `show_logo2 <true|false>`

---

## Source Management

### `get_sources_status`
Get connection status of all input sources (JSON).
```
→ get_sources_status
← ok sources_status {"cam1": true, "cam2": false, "cam3": true, "cam4": false}
```
`true` = client actively connected to that port, `false` = no signal.

### `restart_source <source>`
Restart a disconnected source.
```
→ restart_source cam2
← ok source_restarted cam2
```

---

## Key-Value Store Commands

### `store_value <key> <value>`
Store a value in voctocore's memory. Broadcasts to all clients.
```
→ store_value speaker_name Martin%20García
← notify value speaker_name Martin%20García
```

### `fetch_value <key>`
Retrieve a stored value.
```
→ fetch_value speaker_name
← ok value speaker_name Martin%20García
```

---

## Config Commands

### `get_config`
Returns full parsed server config as JSON.

### `get_config_option <section> <key>`
Returns single config value.
```
→ get_config_option mix sources
← ok server_config_option mix sources cam1, cam2, cam3, cam4
```

---

## Messaging

### `message <args...>`
Send a custom message to all connected clients without changing state. Used for user-defined scripts.
```
→ message production_started 2026-05-13T10:00:00
← notify message production_started 2026-05-13T10:00:00
```

---

## Connection Management

### `help`
Returns all available commands with signatures and descriptions.

### `quit` / `exit`
Close the connection gracefully.

---

## Usage Examples

### Shell (netcat)
```bash
echo "get_video" | nc localhost 9999

# Set source and composite atomically:
echo "set_videos_and_composite cam1 cam2 side_by_side_equal" | nc localhost 9999

# Activate PAUSE blanker:
echo "set_stream_blank pause" | nc localhost 9999

# Restore live:
echo "set_stream_live" | nc localhost 9999
```

### Python client snippet
```python
import socket

def send_command(cmd: str, host: str = "localhost", port: int = 9999) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall((cmd + "\n").encode())
        return s.recv(4096).decode().strip()

print(send_command("get_video"))
print(send_command("set_video_a cam2"))
```
