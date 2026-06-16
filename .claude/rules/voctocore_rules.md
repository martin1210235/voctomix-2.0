# voctocore Rules

Rules for editing code under `voctocore/`.

---

## Pipeline Architecture

- `voctocore/lib/pipeline.py` constructs the entire GStreamer pipeline at startup. Any new module must register itself here.
- GStreamer elements are linked once at init time. Dynamic relinking at runtime requires `set_state(NULL)` first and is avoided.
- All state changes (source switch, composite mode, overlay) go through `commands.py` → the pipeline object → the relevant lib module. Never bypass this chain.

## Module Boundaries

| Module | Responsibility | What it must NOT do |
|--------|---------------|---------------------|
| `videomix.py` | Select/mix video sources, manage compositor | Touch audio state |
| `audiomix.py` | Manage audio volumes and AFV logic | Touch video pipeline |
| `streamblanker.py` | Gate program output (LIVE/PAUSE/NOSTREAM) | Change compositor |
| `overlay.py` | Inject PNG/text overlays | Handle source switching |
| `commands.py` | Parse and dispatch TCP commands | Business logic |
| `controlserver.py` | Manage TCP connections | Execute commands |

## Config Access

- Always read from `Config` (singleton wrapping `default-config.ini`). Never hardcode resolution, framerate, or port numbers.
- Use `Config.getlist()` for comma-separated values. Use `Config.getboolean()` for flags.
- Conditional command registration (stream-blanker, overlay, logo1, logo2) is done at class definition time with `if Config.hasX():` blocks — keep this pattern.

## GStreamer Conventions

- Video caps: `video/x-raw,format=UYVY,width=1920,height=1080,framerate=25/1`
- Audio caps: `audio/x-raw,format=S16LE,rate=48000,channels=2`
- Use `videomixer` (not `compositor`) for backward compatibility. Check config before switching.
- All GStreamer elements must be added to the pipeline bin before linking. Link order matters.

## Testing

- Tests live in `voctocore/tests/` with subdirs `commands/`, `videomix/`, `helper/`.
- All tests use fake GI bindings via `tests/helper/fake-gi.sh` — no real GStreamer needed.
- Run with `./voctocore/test.sh` from project root, or `python3 -m unittest discover -s tests` from inside `voctocore/`.
- When adding a new command to `commands.py`, add a corresponding test in `tests/commands/`.

## Error Handling

- Raise `ValueError` for invalid command arguments (e.g., unknown source name). The control server catches these and sends an error response to the client.
- Log with `self.log = logging.getLogger('ClassName')` — never use `print()`.
- GStreamer pipeline errors must be caught on the bus message handler, not inline.
