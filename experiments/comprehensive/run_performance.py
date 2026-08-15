#!/usr/bin/env python3
"""Analysis 1 (performance) — orchestration driver.

Brings up the stack (realistic BBB config) and, depending on the mode:
  escalado  (1.1): starts cam1, then cam2, cam3, cam4, every --step-min minutes.
  sostenida (1.2): starts all 4 cameras and holds them for --duration-min minutes.
Telemetry records host CPU%/RAM% the whole time in sessions/sessionN.jsonl.
When done, that session is parsed into CSV/summary/XLSX with parse_performance.py.

The video format is set beforehand by set_format.sh (this driver does not touch it).

Usage:
  run_performance.py escalado  <output_dir> [--step-min 15]
  run_performance.py sostenida <output_dir> [--duration-min 120]
  (optional: --keep-up to not tear down the stack at the end)
"""

import argparse
import glob
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE = ["-f", "docker-compose.yml", "-f", "docker-compose.experiment.yml"]
NONCAM = ["rabbitmq", "voctocore", "telemetry", "break", "intro",
          "stream_blanker", "audio_manager"]
CAMS = ["cam1", "cam2", "cam3", "cam4"]


def dc(*args):
    return subprocess.run(["docker", "compose", *BASE, *args],
                          cwd=ROOT, capture_output=True, text=True)


def ctrl(cmd, wait=0.5):
    """Send a voctocore control command (best-effort; only affects what is shown
    on the monitor, not the CPU/RAM measured, since every connected camera is
    processed regardless of what is displayed)."""
    try:
        s = socket.socket(); s.settimeout(2)
        s.connect(("127.0.0.1", 9999)); time.sleep(0.3)
        s.sendall((cmd + "\n").encode()); time.sleep(wait)
        s.close()
    except Exception as e:
        print(f"[perf] ctrl warning '{cmd}': {e}")


def sessions_set():
    return set(glob.glob(os.path.join(ROOT, "sessions", "session*.jsonl")))


def wait_healthy(name, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        out = subprocess.run(["docker", "inspect", "--format",
                              "{{.State.Health.Status}}", name],
                             capture_output=True, text=True).stdout.strip()
        if out == "healthy":
            return True
        time.sleep(2)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["escalado", "sostenida"])
    ap.add_argument("output_dir")
    ap.add_argument("--idle-min", type=float, default=15.0,
                    help="baseline at 0 cameras at the start of scaling")
    ap.add_argument("--step-min", type=float, default=15.0)
    ap.add_argument("--duration-min", type=float, default=120.0)
    ap.add_argument("--keep-up", action="store_true")
    args = ap.parse_args()

    print("[perf] tearing down any previous stack...")
    dc("down")
    time.sleep(2)
    before = sessions_set()

    print("[perf] starting base services (no cameras)...")
    dc("up", "-d", *NONCAM)
    if not wait_healthy("voctocore"):
        print("ERROR: voctocore did not become healthy", file=sys.stderr)
        sys.exit(1)
    # Wait (up to 30s) for telemetry to create its session file.
    session = None
    for _ in range(30):
        time.sleep(1)
        new = sessions_set() - before
        if new:
            session = max(new, key=os.path.getmtime)
            break
    if session is None:
        print("ERROR: telemetry did not create a session file (is SAVE_LOGS=true?).",
              file=sys.stderr)
        dc("logs", "--tail", "20", "telemetry")
        sys.exit(1)
    print(f"[perf] telemetry session: {os.path.basename(session)}")

    # On-screen mix monitor, only if SHOW_GUI=1 (supervised run).
    # In unattended runs, the GUI is NOT opened (avoids hangs and isn't needed).
    if os.environ.get("SHOW_GUI") == "1":
        try:
            subprocess.run(["bash", os.path.join(os.path.dirname(__file__), "show_gui.sh")],
                           cwd=ROOT, timeout=60)
        except Exception:
            pass

    if args.mode == "escalado":
        step = args.step_min * 60
        print(f"[perf] baseline {args.idle_min} min at 0 cameras (t={time.strftime('%H:%M:%S')})...")
        time.sleep(args.idle_min * 60)
        for cam in CAMS:
            print(f"[perf] activating {cam} (t={time.strftime('%H:%M:%S')}), measuring {args.step_min} min...")
            dc("up", "-d", cam)
            time.sleep(8)                 # let the camera connect
            ctrl(f"set_video_a {cam}")    # show it on the monitor (does not affect the measurement)
            time.sleep(max(0, step - 8))
    else:  # sostenida
        print("[perf] activating all 4 cameras...")
        dc("up", "-d", *CAMS)
        time.sleep(8)
        ctrl("set_video_a cam1")
        print(f"[perf] sustained load {args.duration_min} min (t={time.strftime('%H:%M:%S')})...")
        time.sleep(args.duration_min * 60)

    print("[perf] end of the measurement window.")
    # Look for the final session (in case the index changed)
    if session is None:
        after = sessions_set() - before
        session = max(after, key=os.path.getmtime) if after else None
    if session is None:
        print("ERROR: telemetry session not found.", file=sys.stderr)
        sys.exit(1)

    if not args.keep_up:
        print("[perf] tearing down the stack...")
        dc("down")

    label = args.mode
    print(f"[perf] parsing {os.path.basename(session)} -> {args.output_dir}")
    subprocess.run([sys.executable,
                    os.path.join(os.path.dirname(__file__), "parse_performance.py"),
                    session, args.output_dir, "--label", label])


if __name__ == "__main__":
    main()
