#!/usr/bin/env python3
"""24 h sustained run on LOCAL 1080p25 (memory-leak study, analogous to the Docker 4K one).

ROBUST for long duration:
- INCREMENTAL writes: every sample is written and flushed to datos.csv immediately,
  so a failure at hour 20 does NOT lose the 20 h already measured.
- CAMERA HEALTH: every 60 s checks that all 4 native cameras are still alive and
  restarts any that have died (keeps the load constant over 24 h).
- On completion, generates resumen.csv and datos.xlsx.

CPU/RAM are read from /proc (same source as htop), I420 1080p25 format.

Usage:
  sostenida_24h_local.py <output_dir> [--duration-min 1440] [--sample-sec 5]
"""
import argparse
import csv
import os
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib_common import stats, write_summary_csv, bundle_xlsx  # noqa: E402
LOCAL = os.path.join(HERE, "local_scenario.sh")


def read_cpu():
    with open("/proc/stat") as f:
        p = [float(x) for x in f.readline().split()[1:]]
    return p[3], sum(p)


def read_ram():
    m = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":")
            m[k.strip()] = int(v.split()[0])
    return round(100.0 * (m["MemTotal"] - m["MemAvailable"]) / m["MemTotal"], 1)


def local(*args, timeout=180):
    logf = "/tmp/sost24_local.log"
    try:
        with open(logf, "w") as f:
            subprocess.run(["bash", LOCAL, *args], stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    try:
        return open(logf, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def cams_alive():
    """Returns the set of camera numbers (1-4) whose ffmpeg process is still alive."""
    alive = set()
    for n in (1, 2, 3, 4):
        r = subprocess.run(["pgrep", "-f", f"voctolocal_cam{n}"], capture_output=True)
        if r.stdout.strip():
            alive.add(n)
    return alive


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--duration-min", type=float, default=1440.0)
    ap.add_argument("--sample-sec", type=float, default=5.0)
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print("[sost24] setting format 1080p25 and starting Local...", flush=True)
    subprocess.run(["bash", os.path.join(HERE, "set_format.sh"), "1080p25"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local("down")
    r = local("base_up", timeout=200)
    if "base_up OK" not in (r or ""):
        print(f"ERROR: base_up failed:\n{r}", file=sys.stderr)
        local("down")
        sys.exit(1)
    for n in (1, 2, 3, 4):
        local("cam_up", str(n), "experiment")
    time.sleep(10)
    # verify the mix produces video
    subprocess.run("timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 "
                   "-vf 'select=gte(t\\,1)' -frames:v 1 /tmp/sost24_mix.png",
                   shell=True)
    if not (os.path.isfile("/tmp/sost24_mix.png") and os.path.getsize("/tmp/sost24_mix.png") > 1000):
        print("ERROR: the mix produces no video", file=sys.stderr)
        local("down")
        sys.exit(1)
    print(f"[sost24] {len(cams_alive())}/4 cameras up, mix OK. Measuring for {args.duration_min} min...", flush=True)

    fields = ["timestamp", "elapsed_s", "cpu_pct", "ram_pct", "n_cameras_active"]
    csvpath = os.path.join(args.output_dir, "datos.csv")
    f = open(csvpath, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    f.flush()

    t0 = time.time()
    end = t0 + args.duration_min * 60
    idle0, tot0 = read_cpu()
    last_health = t0
    rows = 0
    while time.time() < end:
        time.sleep(args.sample_sec)
        idle1, tot1 = read_cpu()
        dtot = tot1 - tot0
        cpu = round(100.0 * (1.0 - (idle1 - idle0) / dtot), 1) if dtot > 0 else 0.0
        idle0, tot0 = idle1, tot1
        n_active = len(cams_alive())
        w.writerow({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "elapsed_s": int(time.time() - t0), "cpu_pct": cpu,
                    "ram_pct": read_ram(), "n_cameras_active": n_active})
        f.flush()
        os.fsync(f.fileno())
        rows += 1
        # camera health every 60 s
        if time.time() - last_health >= 60:
            dead = {1, 2, 3, 4} - cams_alive()
            for n in dead:
                print(f"[sost24] cam{n} down -> restarting (t={datetime.now():%H:%M:%S})", flush=True)
                local("cam_up", str(n), "experiment")
            last_health = time.time()

    f.close()
    local("down")
    print(f"[sost24] end: {rows} samples. Generating summary/xlsx...", flush=True)

    # summary + xlsx from the complete datos.csv
    data = list(csv.DictReader(open(csvpath, newline="")))
    summary = []
    for metric in ("cpu_pct", "ram_pct"):
        vals = [float(r[metric]) for r in data if r.get(metric)]
        summary.append({"group": "ALL", "metric": metric, **stats(vals)})
    sfields = ["group", "metric", "n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std"]
    write_summary_csv(os.path.join(args.output_dir, "resumen.csv"), summary)
    frows = [{k: r[k] for k in fields} for r in data]
    bundle_xlsx(os.path.join(args.output_dir, "datos.xlsx"),
                {"datos": (fields, frows), "resumen": (sfields, summary)})
    print(f"[sost24] DONE -> {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
