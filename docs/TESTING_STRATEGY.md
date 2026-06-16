# Testing Strategy

## Overview

voctocore has unit tests. voctogui has no automated tests (GUI logic requires manual validation).

---

## voctocore Unit Tests

### Location

```
voctocore/tests/
├── commands/          ← Tests for each TCP command in commands.py
│   ├── test_set_video_a.py
│   ├── test_set_video_b.py
│   ├── test_set_composite_mode.py
│   └── ...
├── videomix/          ← Tests for compositor logic
│   ├── test_composites.py
│   └── ...
└── helper/
    └── fake-gi.sh     ← Mocks gi.repository (GStreamer) so tests run without a display
```

### Running Tests

```bash
# All tests:
./voctocore/test.sh

# All tests with verbose output:
cd voctocore && python3 -m unittest discover -s tests -p 'test_*.py' -v

# Single test module:
cd voctocore && python3 -m unittest tests.commands.test_set_video_a -v

# Single test case:
cd voctocore && python3 -m unittest tests.videomix.test_composites.TestComposites.test_fullscreen -v
```

### Fake GI Bindings

Tests use mock GI bindings so they run without a GStreamer installation or X11 display. The mock is activated by `fake-gi.sh` which sets `PYTHONPATH` to include `tests/helper/`.

Never import from `gi.repository` in test code. The fake replaces `gi`, `Gst`, `GLib`, `GObject`.

---

## Manual Integration Tests

### Scenario 1 — Native single PC

```bash
./start_studio_single_pc.sh
# Verify: voctogui opens, 6 previews visible, source switching works
```

### Scenario 2 — Two PCs

```bash
# PC1:
./2pc_escenario2/start_voctocore_pc1.sh

# PC2:
IP_SERVER=<PC1_IP> ./2pc_escenario2/start_voctogui_pc2.sh
# Verify: remote connection established, no latency visible
```

### Scenario 3 — Docker

```bash
xhost +local:$(id -un)
./launch_docker_studio.sh
docker compose ps            # all 10 services healthy
docker compose logs voctocore | tail -20
```

---

## Telemetry Validation

```bash
# Native: check that JSON is written every second
tail -f registros/gui_state.json

# Docker: check RabbitMQ receives messages
# Navigate to http://localhost:15672 (guest:guest or voctomix:voctomix123)
# → Overview → Message Rates should show activity
```

---

## Lint

```bash
./check_pep8.sh   # pycodestyle, exits non-zero on violations
```

PEP8 ignores:
- `E402` — module-level import order (gi requires `require_version` before import)
- `E501` in test files — long assertion strings

---

## Adding New Tests

When adding a new command to `commands.py`:

1. Create `voctocore/tests/commands/test_<command_name>.py`
2. Import `unittest` and the command class
3. Use `fake-gi.sh` environment (already handled by `test.sh`)
4. Test: valid arguments, invalid arguments (should raise `ValueError`), response type (`OkResponse` vs `NotifyResponse`)

Example skeleton:
```python
import unittest
from unittest.mock import MagicMock
from lib.commands import ControlServerCommands

class TestSetVideoA(unittest.TestCase):
    def setUp(self):
        self.pipeline = MagicMock()
        self.pipeline.vmix.getVideoSources.return_value = ['cam1', 'cam2']
        self.cmd = ControlServerCommands(self.pipeline)

    def test_set_valid_source(self):
        response = self.cmd.set_video_a('cam2')
        self.pipeline.vmix.setVideoSourceA.assert_called_once_with('cam2')
```
