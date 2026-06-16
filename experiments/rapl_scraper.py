#!/usr/bin/env python3
"""
Reads Intel RAPL energy counters every INTERVAL seconds and appends
{"type": "power", "watts_rapl": X.X} entries to the active session .jsonl.

RAPL (Running Average Power Limit) is the hardware energy sensor built into
Intel CPUs. It measures actual package power consumed, unlike the TDP-based
estimate which assumes linear scaling and ignores turbo boost and power gating.

Runs on the host (no Docker needed). Requires read access to:
  /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj

Usage:
    python3 experiments/rapl_scraper.py <session.jsonl> [interval_s]
    Defaults: interval=5s (matches STATE event cadence)
"""
import sys
import time
import json
from datetime import datetime
from pathlib import Path

RAPL_PATH    = Path("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj")
MAX_RANGE_PATH = Path("/sys/class/powercap/intel-rapl/intel-rapl:0/max_energy_range_uj")


def read_energy_uj() -> int:
    return int(RAPL_PATH.read_text().strip())


def read_max_range() -> int:
    return int(MAX_RANGE_PATH.read_text().strip())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    interval   = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    if not RAPL_PATH.exists():
        print("[rapl] ERROR: RAPL not available at", RAPL_PATH)
        sys.exit(1)

    max_range = read_max_range()
    print(f"[rapl] RAPL available. max_energy_range = {max_range/1e6:.0f} kJ")
    print(f"[rapl] Writing to {jsonl_path} every {interval}s")

    prev_uj = read_energy_uj()
    prev_t  = time.monotonic()

    while True:
        time.sleep(interval)

        curr_uj = read_energy_uj()
        curr_t  = time.monotonic()

        delta_uj = curr_uj - prev_uj
        # Handle counter wraparound
        if delta_uj < 0:
            delta_uj += max_range

        elapsed  = curr_t - prev_t
        watts    = round(delta_uj / elapsed / 1e6, 2)

        prev_uj = curr_uj
        prev_t  = curr_t

        entry = {
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type":       "power",
            "watts_rapl": watts,
            "delta_uj":   delta_uj,
            "interval_s": round(elapsed, 3),
        }

        try:
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            print(f"[rapl] {entry['timestamp']}  {watts:.2f} W", flush=True)
        except Exception as e:
            print(f"[rapl] Warning: {e}", flush=True)


if __name__ == "__main__":
    main()
