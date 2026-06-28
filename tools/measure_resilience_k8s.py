#!/usr/bin/env python3
"""
Measures Kubernetes container recovery time after a forced kill.

For each iteration:
  1. Record t_kill  — kubectl exec <pod> -c <container> -- kill -9 1
  2. Poll kubectl get pod until the container is ready=true again
  3. Record t_ready
  4. Recovery time = t_ready - t_kill
  5. Wait --wait seconds before next iteration (default: 720 s = 12 min)
     This ensures Kubernetes resets the CrashLoopBackOff counter between
     iterations (threshold: container running > 10 min without crashing).
     Use --wait 30 for a quick test that shows CrashLoopBackOff progression.

Requirements: kubectl configured and pointing to a running cluster.

Usage:
    python3 tools/measure_resilience_k8s.py [--container cam1] [--n 5] [--wait 720]
"""

import subprocess
import time
import json
import argparse
from datetime import datetime


def get_pod_name():
    result = subprocess.run(
        ["kubectl", "get", "pods", "-l", "app=studio",
         "--field-selector=status.phase=Running",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True
    )
    name = result.stdout.strip()
    if not name:
        raise RuntimeError(
            "No running studio pod found. Is Minikube running? "
            "Check: kubectl get pods -l app=studio"
        )
    return name


def container_is_ready(pod, container):
    result = subprocess.run(
        ["kubectl", "get", "pod", pod, "-o", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False
    try:
        data = json.loads(result.stdout)
        for cs in data.get("status", {}).get("containerStatuses", []):
            if cs["name"] == container:
                return cs.get("ready", False)
    except (json.JSONDecodeError, KeyError):
        pass
    return False


def measure_recovery(pod, container, n, wait_between):
    results = []
    print(f"Pod: {pod}  |  Container: {container}  |  {n} iterations  |  {wait_between}s between kills\n")

    for i in range(n):
        print(f"[{i+1:02d}/{n}] Killing PID 1 in container '{container}'...")
        kill_result = subprocess.run(
            ["kubectl", "exec", pod, "-c", container, "--", "kill", "-9", "1"],
            capture_output=True, text=True
        )
        t_kill = time.monotonic()

        if kill_result.returncode != 0:
            print(f"       WARNING: kill command returned {kill_result.returncode}: {kill_result.stderr.strip()}")

        deadline = t_kill + 120
        recovered = False
        while time.monotonic() < deadline:
            time.sleep(0.5)
            if container_is_ready(pod, container):
                t_ready = time.monotonic()
                recovered = True
                break

        if not recovered:
            print(f"       TIMEOUT: container did not recover within 120 s.")
            print("       This may indicate CrashLoopBackOff with max backoff (5 min).")
            print("       Consider re-running with a longer --wait value.")
            continue

        ms = round((t_ready - t_kill) * 1000)
        results.append(ms)
        print(f"       Recovered in {ms} ms")

        if i < n - 1:
            print(f"       Waiting {wait_between}s before next iteration "
                  f"(CrashLoopBackOff reset threshold: 600s)...")
            for remaining in range(wait_between, 0, -30):
                time.sleep(min(30, remaining))
                if remaining > 30:
                    print(f"       ... {remaining - 30}s remaining")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Measure Kubernetes container recovery time."
    )
    parser.add_argument("--container", default="cam1",
                        help="Container name to kill (default: cam1)")
    parser.add_argument("--n", type=int, default=5,
                        help="Number of iterations (default: 5)")
    parser.add_argument("--wait", type=int, default=720,
                        help="Seconds between iterations (default: 720 = 12 min). "
                             "Use >= 600 to avoid CrashLoopBackOff backoff between kills.")
    parser.add_argument("--output", default="sessions/resilience_cam1_k8s.json",
                        help="Output JSON path (default: sessions/resilience_cam1_k8s.json)")
    args = parser.parse_args()

    print("=" * 60)
    print("  Voctomix K8s Resilience Test")
    print(f"  Container: {args.container}  |  Iterations: {args.n}")
    total_min = (args.n * (args.wait + 5)) / 60
    print(f"  Estimated duration: ~{total_min:.0f} min")
    if args.wait < 600:
        print("  WARNING: --wait < 600s. CrashLoopBackOff may affect later iterations.")
        print("           Recovery times will increase: 10s, 20s, 40s, 80s, 160s, 300s...")
    print("=" * 60)
    print()

    pod = get_pod_name()
    print(f"Found pod: {pod}")

    if not container_is_ready(pod, args.container):
        print(f"ERROR: Container '{args.container}' is not Ready. "
              "Wait for it to be healthy before running the test.")
        raise SystemExit(1)
    print(f"Container '{args.container}' is Ready. Starting test...\n")

    results = measure_recovery(pod, args.container, args.n, args.wait)

    if not results:
        print("\nNo successful measurements.")
        return

    import numpy as np
    vals = np.array(results)
    print("\n" + "=" * 60)
    print("  RESULTS (ms)")
    print("=" * 60)
    print(f"  n            : {len(vals)}")
    print(f"  min          : {np.min(vals)}")
    print(f"  median       : {np.median(vals):.0f}")
    print(f"  mean         : {np.mean(vals):.0f}")
    print(f"  max          : {np.max(vals)}")
    print(f"  p95          : {np.percentile(vals, 95):.0f}")
    print(f"  raw (ms)     : {list(map(int, vals))}")
    print()

    docker_median = 520
    k8s_median = float(np.median(vals))
    print(f"  Docker median  : {docker_median} ms")
    print(f"  K8s median     : {k8s_median:.0f} ms")
    print(f"  K8s / Docker   : {k8s_median / docker_median:.1f}×")

    output = {
        "environment": "kubernetes",
        "container": args.container,
        "pod": pod,
        "timestamp": datetime.now().isoformat(),
        "wait_between_s": args.wait,
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
    out_path = args.output
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
