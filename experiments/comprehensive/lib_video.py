#!/usr/bin/env python3
"""Live video tap for latency/recovery detection.

Reads the composited mix output (voctocore raw mix, port 11000), crops the
top-left corner (where each camera burns a distinct colour marker) and exposes
the most-recent (timestamp, mean_rgb) so callers can time when a switch or a
recovery becomes visible. Bandwidth is bounded by the crop, so it works the
same at 1080p and 2160p.

Camera colour markers (see docker-compose.experiment.yml):
  cam1=red  cam2=green(lime)  cam3=blue  cam4=yellow ; no source -> black
"""

import subprocess
import threading
import time

import numpy as np

# Reference colours for nearest-match classification.
REFS = {
    "cam1": (255, 0, 0),     # red
    "cam2": (0, 255, 0),     # green / lime
    "cam3": (0, 0, 255),     # blue
    "cam4": (255, 255, 0),   # yellow
    "none": (0, 0, 0),       # black = no source / blanked
}


def classify(rgb):
    """Nearest reference colour -> camera id (or 'none')."""
    r, g, b = rgb
    best, bestd = "none", 1e18
    for name, (rr, gg, bb) in REFS.items():
        d = (r - rr) ** 2 + (g - gg) ** 2 + (b - bb) ** 2
        if d < bestd:
            best, bestd = name, d
    return best


class MixCornerReader:
    """Background reader of a small region of the mix output.
    current() -> (t_monotonic, (r,g,b)).

    Defaults to the top-left 300x300 corner (camera colour marker, Análisis 2.1
    and 3.1). Pass w/h/x/y (x/y accept ffmpeg expressions like 'iw*0.75-60') to
    sample another region, e.g. right-centre for fs/sbs detection (Análisis 2.2).
    """

    def __init__(self, port=11000, host="127.0.0.1", w=300, h=300, x="0", y="0"):
        self.w, self.h = w, h
        self.frame_bytes = w * h * 3
        cmd = [
            "ffmpeg", "-nostdin", "-loglevel", "error",
            "-fflags", "nobuffer", "-flags", "low_delay",
            "-i", f"tcp://{host}:{port}",
            "-vf", f"crop={w}:{h}:{x}:{y}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, bufsize=0)
        self._latest = (None, None)
        self._lock = threading.Lock()
        self._running = True
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    def _read_exact(self, n):
        buf = bytearray()
        while len(buf) < n:
            chunk = self.proc.stdout.read(n - len(buf))
            if not chunk:
                return None
            buf.extend(chunk)
        return bytes(buf)

    def _loop(self):
        while self._running:
            buf = self._read_exact(self.frame_bytes)
            if buf is None:
                break
            t = time.monotonic()
            arr = np.frombuffer(buf, dtype=np.uint8)
            mean = tuple(int(x) for x in arr.reshape(-1, 3).mean(axis=0))
            with self._lock:
                self._latest = (t, mean)

    def current(self):
        with self._lock:
            return self._latest

    def wait_until(self, predicate, after_t, timeout=8.0, poll=0.001):
        """Return (t, rgb) of the first frame with t>after_t where
        predicate(classify(rgb)) is True, else None on timeout."""
        deadline = time.monotonic() + timeout
        seen_t = after_t
        while time.monotonic() < deadline:
            t, rgb = self.current()
            if t is not None and t > seen_t and rgb is not None:
                seen_t = t
                if predicate(classify(rgb)):
                    return (t, rgb)
            time.sleep(poll)
        return None

    def alive(self):
        return self.proc.poll() is None

    def stop(self):
        self._running = False
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
