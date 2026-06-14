#!/usr/bin/env python3
"""
Measures voctocore switching latency by sending set_video_a commands over TCP
and timing the response. Appends results as {"type":"latency"} entries to the
active session .jsonl so analyze_cameras.py can process them together.

Intended to run in parallel during the N=4 camera experiment.

Usage:
    python3 experiments/measure_latency.py <session.jsonl> [host] [port]

Defaults: host=localhost, port=9999, 30 measurements with 4-second intervals.
"""
import socket
import time
import json
import sys
from datetime import datetime

HOST   = "localhost"
PORT   = 9999
REPS   = 30
INTERVAL = 4.0   # seconds between switches
TIMEOUT  = 2.0   # seconds to wait for video_status response

SOURCES = ["cam1", "cam2", "cam3", "cam4"]


def current_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def measure_one(sock, buf: list[str], target_cam: str) -> float | None:
    cmd = f"set_video_a {target_cam}\n".encode()
    t0 = time.perf_counter()
    sock.sendall(cmd)

    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            chunk = sock.recv(4096).decode("utf-8", errors="replace")
        except socket.timeout:
            continue
        if not chunk:
            return None
        buf.append(chunk)
        combined = "".join(buf)
        lines = combined.split("\n")
        buf.clear()
        buf.append(lines[-1])
        for line in lines[:-1]:
            line = line.strip()
            if line.startswith("video_status"):
                t1 = time.perf_counter()
                return round((t1 - t0) * 1000, 2)

    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else HOST
    port = int(sys.argv[3]) if len(sys.argv) > 3 else PORT

    print(f"[latency] Connecting to {host}:{port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    for attempt in range(10):
        try:
            sock.connect((host, port))
            break
        except (ConnectionRefusedError, OSError):
            print(f"[latency] Waiting for voctocore ({attempt+1}/10)...")
            time.sleep(3)
    else:
        print("[latency] Could not connect. Aborting.")
        sys.exit(1)

    print(f"[latency] Connected. Running {REPS} measurements ...")

    buf = []
    results = []

    # Drain initial state messages
    sock.settimeout(2.0)
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
    except socket.timeout:
        pass

    sock.settimeout(TIMEOUT)

    for i in range(REPS):
        src = SOURCES[i % len(SOURCES)]
        latency_ms = measure_one(sock, buf, src)

        if latency_ms is not None:
            results.append(latency_ms)
            status = f"{latency_ms:.1f} ms"
        else:
            status = "timeout"

        print(f"[latency] {i+1:2d}/{REPS}  set_video_a {src}  → {status}")

        entry = {
            "timestamp": current_ts(),
            "type": "latency",
            "target_cam": src,
            "latency_ms": latency_ms,
            "measurement_index": i + 1,
        }
        try:
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[latency] Warning: could not write to {jsonl_path}: {e}")

        time.sleep(INTERVAL)

    sock.close()

    valid = [r for r in results if r is not None]
    if valid:
        import statistics
        valid_sorted = sorted(valid)
        n = len(valid_sorted)
        p50 = statistics.median(valid_sorted)
        p95 = valid_sorted[int(n * 0.95)]
        print(f"\n[latency] Results ({n}/{REPS} valid):")
        print(f"  Median (p50): {p50:.1f} ms")
        print(f"  p95:          {p95:.1f} ms")
        print(f"  Min:          {min(valid_sorted):.1f} ms")
        print(f"  Max:          {max(valid_sorted):.1f} ms")
    else:
        print("[latency] No valid measurements.")


if __name__ == "__main__":
    main()
