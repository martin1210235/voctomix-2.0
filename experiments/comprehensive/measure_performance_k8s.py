#!/usr/bin/env python3
"""Analysis 1 (performance) for the KUBERNETES (k3s) scenario.

Measures host CPU%/RAM% by reading /proc (same method as Local/Docker; the pods
run on the host with hostNetwork, so global /proc = k3s + pods = deployment
consumption). Orchestrates the scenario with k8s_scenario.sh.

  escalado  (1.1): --idle-min min baseline at 0 cameras, then activates cam1..4
                   (kubectl scale) one every --step-min min. Labelled by number active.
  sostenida (1.2): 4 cameras for --duration-min min.

Outputs: datos.csv, resumen.csv, datos.xlsx (same format as Local/Docker).

Usage:
  measure_performance_k8s.py <escalado|sostenida> <output_dir> --format 1080p25 \
      [--idle-min 15] [--step-min 15] [--duration-min 120]
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_common import stats, write_csv, write_summary_csv, bundle_xlsx  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
K8S = os.path.join(HERE, "..", "..", "k8s_escenario", "experiments", "k8s_scenario.sh")


def read_cpu():
    with open("/proc/stat") as f:
        parts = [float(x) for x in f.readline().split()[1:]]
    return parts[3], sum(parts)


def read_ram():
    m = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":")
            m[k.strip()] = int(v.split()[0])
    return round(100.0 * (m["MemTotal"] - m["MemAvailable"]) / m["MemTotal"], 1)


def k8s(*args, timeout=300):
    logf = "/tmp/k8s_scn_perf.log"
    try:
        with open(logf, "w") as f:
            subprocess.run(["bash", K8S, *args],
                           stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    try:
        return open(logf, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["escalado", "sostenida"])
    ap.add_argument("output_dir")
    ap.add_argument("--format", required=True,
                    choices=["1080p25", "1080p50", "2160p25", "2160p50"])
    ap.add_argument("--idle-min", type=float, default=15.0,
                    help="baseline at 0 cameras (scaling only)")
    ap.add_argument("--step-min", type=float, default=15.0)
    ap.add_argument("--duration-min", type=float, default=120.0)
    args = ap.parse_args()

    print(f"[perf-k8s] up {args.format} (voctocore + support)...", flush=True)
    out = k8s("up", args.format, timeout=300)
    if "successfully rolled out" not in out and "waiting for voctocore" not in out:
        print(f"ERROR: up failed:\n{out}", file=sys.stderr)
        k8s("down"); sys.exit(1)

    n_active = 0
    rows = []
    idle0, tot0 = read_cpu()
    t0 = time.time()

    def sample():
        nonlocal idle0, tot0
        idle1, tot1 = read_cpu()
        dtot = tot1 - tot0
        cpu = round(100.0 * (1.0 - (idle1 - idle0) / dtot), 1) if dtot > 0 else 0.0
        idle0, tot0 = idle1, tot1
        rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_s": int(time.time() - t0),
            "cpu_pct": cpu, "ram_pct": read_ram(),
            "n_cameras_active": n_active,
        })

    def measure_for(seconds):
        end = time.time() + seconds
        read_cpu()
        while time.time() < end:
            time.sleep(5)
            sample()

    if args.mode == "escalado":
        k8s("apply-cams", args.format, "experiment", timeout=120)
        print(f"[perf-k8s] baseline {args.idle_min} min at 0 cameras", flush=True)
        n_active = 0
        measure_for(args.idle_min * 60)
        for cam in (1, 2, 3, 4):
            print(f"[perf-k8s] activating cam{cam} (t={datetime.now():%H:%M:%S})", flush=True)
            k8s("scale", str(cam), "1", timeout=60)
            time.sleep(8)
            n_active = cam
            measure_for(args.step_min * 60 - 8)
    else:
        k8s("cams", args.format, "experiment", timeout=240)
        n_active = 4
        time.sleep(6)
        print(f"[perf-k8s] sustained {args.duration_min} min at 4 cameras", flush=True)
        measure_for(args.duration_min * 60)

    k8s("down", timeout=180)

    if not rows:
        print("ERROR: no samples", file=sys.stderr)
        sys.exit(1)

    fields = ["timestamp", "elapsed_s", "cpu_pct", "ram_pct", "n_cameras_active"]
    summary = []
    for metric in ("cpu_pct", "ram_pct"):
        summary.append({"group": "ALL", "metric": metric, **stats([r[metric] for r in rows])})
    for n in sorted({r["n_cameras_active"] for r in rows}):
        sub = [r for r in rows if r["n_cameras_active"] == n]
        for metric in ("cpu_pct", "ram_pct"):
            summary.append({"group": f"{n}_cams", "metric": metric, **stats([r[metric] for r in sub])})
    sfields = ["group", "metric", "n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std"]

    os.makedirs(args.output_dir, exist_ok=True)
    write_csv(os.path.join(args.output_dir, "datos.csv"), fields, rows)
    write_summary_csv(os.path.join(args.output_dir, "resumen.csv"), summary)
    bundle_xlsx(os.path.join(args.output_dir, "datos.xlsx"),
                {"datos": (fields, rows), "resumen": (sfields, summary)})
    print(f"[perf-k8s] {len(rows)} samples -> {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
