#!/usr/bin/env python3
"""
Measures composite transition latency: time from sending 'transition <mode>'
to receiving the 'composite <mode>' confirmation from voctocore.

Usage:
    python3 tools/measure_composite_latency.py [--host HOST] [--port PORT] [--n N]

Defaults: host=localhost, port=9999, n=32 measurements
"""

import socket
import time
import argparse
import json
import numpy as np
from datetime import datetime

MODES = ["fs", "sbs", "pip", "lec"]
SRC_A = "cam1"
SRC_B = "cam2"


def send_recv(sock, cmd, expected_prefix, timeout=3.0):
    sock.sendall((cmd + "\n").encode())
    buf = ""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            chunk = sock.recv(4096).decode(errors="replace")
            buf += chunk
            for line in buf.split("\n"):
                line = line.strip()
                if line.startswith(expected_prefix):
                    return line
        except socket.timeout:
            continue
    return None


def measure(host, port, n_measurements):
    results = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    sock.connect((host, port))

    print(f"Connected to {host}:{port}")
    print(f"Running {n_measurements} transition measurements...\n")

    for i in range(n_measurements):
        mode = MODES[i % len(MODES)]
        cmd = f"transition {mode}({SRC_A},{SRC_B})"
        expected = f"composite {mode}"

        t0 = time.monotonic()
        response = send_recv(sock, cmd, expected)
        t1 = time.monotonic()

        if response is None:
            print(f"  [{i+1:02d}] {mode:4s}  → TIMEOUT")
            continue

        ms = (t1 - t0) * 1000
        results.append({"mode": mode, "latency_ms": round(ms, 3)})
        print(f"  [{i+1:02d}] {mode:4s}  {ms:.2f} ms")
        time.sleep(0.15)

    sock.close()
    return results


def stats(results):
    if not results:
        return {}
    vals = [r["latency_ms"] for r in results]
    return {
        "n": len(vals),
        "min_ms": round(float(np.min(vals)), 2),
        "median_ms": round(float(np.median(vals)), 2),
        "mean_ms": round(float(np.mean(vals)), 2),
        "max_ms": round(float(np.max(vals)), 2),
        "std_ms": round(float(np.std(vals)), 2),
        "p95_ms": round(float(np.percentile(vals, 95)), 2),
    }


def histogram(results, bins=None):
    if bins is None:
        bins = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0]
    vals = [r["latency_ms"] for r in results]
    hist = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        count = sum(1 for v in vals if lo <= v < hi)
        hist[f"{lo}-{hi}"] = count
    return hist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--n", type=int, default=32)
    parser.add_argument("--label", default="docker")
    args = parser.parse_args()

    results = measure(args.host, args.port, args.n)
    s = stats(results)
    h = histogram(results)

    print("\n--- RESULTS ---")
    print(f"  n        : {s['n']}")
    print(f"  min      : {s['min_ms']} ms")
    print(f"  median   : {s['median_ms']} ms")
    print(f"  mean     : {s['mean_ms']} ms")
    print(f"  max      : {s['max_ms']} ms")
    print(f"  std      : {s['std_ms']} ms")
    print(f"  p95      : {s['p95_ms']} ms")
    print(f"\n--- HISTOGRAM ---")
    for bucket, count in h.items():
        bar = "#" * count
        print(f"  {bucket:9s} ms: {bar} ({count})")

    output = {
        "label": args.label,
        "timestamp": datetime.now().isoformat(),
        "host": args.host,
        "port": args.port,
        "stats": s,
        "histogram": h,
        "raw": results,
    }
    out_path = f"sessions/composite_latency_{args.label}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
