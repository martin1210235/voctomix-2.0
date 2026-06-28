#!/usr/bin/env python3
"""
Measures container recovery time after a forced failure.

Process per iteration:
  1. Record t_stop  — docker stop <container>
  2. Poll docker inspect until Status == 'running' and Health == 'healthy'
  3. Record t_healthy
  4. Recovery time = t_healthy - t_stop

Usage:
    python3 tools/measure_resilience.py [--container cam1] [--n 10]
"""

import subprocess
import time
import json
import argparse
import numpy as np
from datetime import datetime


def container_is_healthy(name):
    out = subprocess.run(
        ["docker", "inspect", "--format",
         "{{.State.Status}} {{.State.Health.Status}}", name],
        capture_output=True, text=True
    ).stdout.strip()
    return out == "running healthy"


def measure_recovery(container, n):
    results = []
    print(f"Container: {container}  |  {n} iterations\n")

    for i in range(n):
        # Kill PID 1 inside the container to simulate a real crash.
        # docker stop would set desired-state=stopped and skip restart policy.
        subprocess.run(["docker", "exec", container, "kill", "-9", "1"],
                       capture_output=True)
        t_stop = time.monotonic()

        # Poll until healthy (max 60 s)
        deadline = t_stop + 60
        recovered = False
        while time.monotonic() < deadline:
            time.sleep(0.5)
            if container_is_healthy(container):
                t_healthy = time.monotonic()
                recovered = True
                break

        if not recovered:
            print(f"  [{i+1:02d}] TIMEOUT (>60 s)")
            continue

        ms = round((t_healthy - t_stop) * 1000)
        results.append(ms)
        print(f"  [{i+1:02d}] {ms} ms")
        time.sleep(2)  # brief pause between iterations

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--container", default="cam1")
    parser.add_argument("--n", type=int, default=10)
    args = parser.parse_args()

    results = measure_recovery(args.container, args.n)

    if not results:
        print("No successful measurements.")
        return

    vals = np.array(results)
    print("\n--- RESULTS (ms) ---")
    print(f"  n       : {len(vals)}")
    print(f"  min     : {np.min(vals)}")
    print(f"  median  : {np.median(vals):.0f}")
    print(f"  mean    : {np.mean(vals):.0f}")
    print(f"  max     : {np.max(vals)}")
    print(f"  p95     : {np.percentile(vals, 95):.0f}")

    output = {
        "container": args.container,
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "n": int(len(vals)),
            "min_ms": int(np.min(vals)),
            "median_ms": float(np.median(vals)),
            "mean_ms": float(np.mean(vals)),
            "max_ms": int(np.max(vals)),
            "p95_ms": float(np.percentile(vals, 95)),
        },
        "raw_ms": list(map(int, vals)),
    }
    out_path = f"sessions/resilience_{args.container}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
