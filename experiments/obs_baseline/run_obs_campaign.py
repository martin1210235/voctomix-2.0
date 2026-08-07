#!/usr/bin/env python3
"""
OBS Studio baseline campaign orchestrator for the Voctomix 2.0 paper comparison.

Fully automated equivalent of measure_obs.py (same sampling math, same CSV
schema), but instead of waiting on operator ENTER key-presses per phase, it
launches OBS itself once per phase (--profile/--collection/--scene/--startrecording),
matching the pre-built "obs_baseline" profile and scene collection:
  - Profile "obs_baseline": Simple Output, x264 SOFTWARE encoder, CBR 8000 kbps,
    preset veryfast, canvas 1920x1080 @ 25/1 fps.
  - Scene collection "obs_baseline": 5 scenes (0_cams..4_cams), each compositing
    N media sources (same bbb_sunflower_2160p_60fps_normal.mp4 master used by the
    Voctomix local escalado test) in a 2x2 grid, software-decoded (hw_decode=false).

Whole-host CPU (%) and RAM (%) are read from /proc at 1 Hz, exactly as in
measure_obs.py and in the Voctomix escalado test, so all three tables merge
directly.

Usage:
    python3 run_obs_campaign.py [--warmup 20] [--window 300]
"""
import argparse
import csv
import os
import platform
import signal
import socket
import statistics
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REC_DIR = os.path.join(HERE, "recordings")
PROFILE = "obs_baseline"
COLLECTION = "obs_baseline"

PHASES = ["0_cams", "1_cams", "2_cams", "3_cams", "4_cams"]


def read_cpu_totals():
    with open("/proc/stat") as f:
        fields = f.readline().split()[1:]
    vals = [float(x) for x in fields]
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0.0)
    return sum(vals), idle


def read_mem():
    total = avail = None
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                total = float(line.split()[1])
            elif line.startswith("MemAvailable:"):
                avail = float(line.split()[1])
            if total is not None and avail is not None:
                break
    used_kb = total - avail
    return used_kb / total * 100.0, used_kb / 1048576.0, total / 1048576.0


def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def summarize(group, metric, values):
    s = sorted(values)
    return [
        group, metric, len(s),
        round(min(s), 3), round(percentile(s, 25), 3), round(percentile(s, 50), 3),
        round(percentile(s, 75), 3), round(percentile(s, 95), 3), round(percentile(s, 99), 3),
        round(max(s), 3), round(statistics.mean(s), 3),
        round(statistics.pstdev(s), 3),
    ]


def capture_metadata(args):
    lines = [
        f"timestamp_start   : {datetime.now().isoformat(timespec='seconds')}",
        f"hostname          : {socket.gethostname()}",
        f"platform          : {platform.platform()}",
        f"python            : {platform.python_version()}",
        f"warmup_seconds    : {args.warmup}",
        f"window_seconds    : {args.window}",
        "measurement       : whole-host CPU% (/proc/stat) and RAM% (/proc/meminfo), 1 Hz",
        "orchestration     : automated (OBS launched fresh per phase via --scene, "
        "no manual key-presses)",
        "source_material   : bbb_sunflower_2160p_60fps_normal.mp4 (same master used by "
        "the Voctomix local 1080p25 escalado test); OBS decodes+scales it in software "
        "(hw_decode=false), matching the whole-host CPU cost that the external ffmpeg "
        "source-simulator processes contribute to the Voctomix measurement.",
        "encoder           : x264 software (obs-x264.so), preset veryfast, CBR 8000 kbps, "
        "1920x1080 @ 25/1 -- NVENC NOT used (verified in OBS log per phase).",
    ]
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    lines.append(f"cpu_model         : {line.split(':', 1)[1].strip()}")
                    break
        lines.append(f"logical_cpus      : {os.cpu_count()}")
    except Exception:
        pass
    _, _, total_gb = read_mem()
    lines.append(f"ram_total_gb      : {total_gb:.1f}")
    for cmd, tag in ((["obs", "--version"], "obs_version"),
                     (["uname", "-r"], "kernel"),
                     (["nvidia-smi", "-L"], "gpu")):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            val = (out.stdout or out.stderr).strip().splitlines()
            lines.append(f"{tag:18}: {val[0] if val else 'unknown'}")
        except Exception:
            lines.append(f"{tag:18}: unknown")
    return lines


def obs_running_pid():
    r = subprocess.run(["pgrep", "-x", "obs"], capture_output=True, text=True)
    pids = [int(p) for p in r.stdout.split() if p.strip()]
    return pids[0] if pids else None


def launch_obs(scene, logpath):
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    f = open(logpath, "w")
    proc = subprocess.Popen(
        ["obs", "--profile", PROFILE, "--collection", COLLECTION,
         "--scene", scene, "--startrecording", "--minimize-to-tray",
         "--disable-missing-files-check"],
        env=env, stdout=f, stderr=subprocess.STDOUT,
    )
    return proc, f


def stop_obs_gracefully(proc, grace=12):
    pid = obs_running_pid()
    if pid is None:
        return
    os.kill(pid, signal.SIGTERM)
    t0 = time.time()
    while time.time() - t0 < grace:
        if obs_running_pid() is None:
            return
        time.sleep(0.5)
    remaining = obs_running_pid()
    if remaining is not None:
        os.kill(remaining, signal.SIGKILL)
        time.sleep(1)


def sample_phase(group, warmup, window):
    print(f"  warm-up {warmup}s (discarded)...", end="", flush=True)
    t_prev, i_prev = read_cpu_totals()
    time.sleep(1)
    for _ in range(warmup - 1):
        t_prev, i_prev = read_cpu_totals()
        time.sleep(1)
    print(f" sampling {window}s...", end="", flush=True)
    rows = []
    for _ in range(window):
        t_now, i_now = read_cpu_totals()
        dt, di = t_now - t_prev, i_now - i_prev
        cpu = 100.0 * (dt - di) / dt if dt else 0.0
        used_pct, used_gb, _ = read_mem()
        rows.append((group, round(cpu, 3), round(used_pct, 3), round(used_gb, 3)))
        t_prev, i_prev = t_now, i_now
        time.sleep(1)
    print(" done.")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--window", type=int, default=300)
    args = ap.parse_args()
    os.makedirs(REC_DIR, exist_ok=True)

    print("=" * 68)
    print(" OBS baseline campaign (automated) --- Voctomix 2.0 paper comparison")
    print("=" * 68)
    meta = capture_metadata(args)
    print("\n".join(meta))
    print()

    all_rows = []
    for phase in PHASES:
        # ensure nothing stale running
        stale = obs_running_pid()
        if stale:
            os.kill(stale, signal.SIGKILL)
            time.sleep(1)
        logpath = os.path.join(HERE, f"obs_log_{phase}.txt")
        print(f"[{phase}] launching OBS (scene={phase}, recording ON)...", flush=True)
        proc, logf = launch_obs(phase, logpath)
        time.sleep(6)  # let OBS init GL + start recording before sampling
        rows = sample_phase(phase, args.warmup, args.window)
        all_rows += rows
        print(f"[{phase}] stopping OBS...", flush=True)
        stop_obs_gracefully(proc)
        logf.close()
        # sanity: confirm x264 (not nvenc) actually engaged for this phase
        with open(logpath, encoding="utf-8", errors="replace") as f:
            txt = f.read()
        enc_line = [ln for ln in txt.splitlines() if "x264 encoder" in ln and "preset" in ln]
        print(f"[{phase}] encoder check: {enc_line[0] if enc_line else 'NOT FOUND (check log!)'}")
        time.sleep(2)

    with open(os.path.join(HERE, "obs_datos.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "cpu_pct", "ram_pct", "ram_gb"])
        w.writerows(all_rows)

    resumen = []
    for group in PHASES:
        cpu = [r[1] for r in all_rows if r[0] == group]
        ram = [r[2] for r in all_rows if r[0] == group]
        resumen.append(summarize(group, "cpu_pct", cpu))
        resumen.append(summarize(group, "ram_pct", ram))
    with open(os.path.join(HERE, "obs_resumen.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "metric", "n", "min", "q1", "median", "q3",
                    "p95", "p99", "max", "mean", "std"])
        w.writerows(resumen)

    with open(os.path.join(HERE, "obs_metadata.txt"), "w") as f:
        f.write("\n".join(meta) + f"\ntimestamp_end     : {datetime.now().isoformat(timespec='seconds')}\n")

    total_gb = read_mem()[2]
    print("\n" + "=" * 68)
    print(" SUMMARY")
    print("=" * 68)
    print(f"{'phase':8} {'CPU% med':>9} {'RAM% med':>9} {'RAM GB':>8}")
    for group in PHASES:
        cpu = sorted(r[1] for r in all_rows if r[0] == group)
        rp = sorted(r[2] for r in all_rows if r[0] == group)
        rg = sorted(r[3] for r in all_rows if r[0] == group)
        print(f"{group:8} {percentile(cpu, 50):>9.1f} {percentile(rp, 50):>9.1f} {percentile(rg, 50):>8.1f}")
    print(f"\n(host RAM total: {total_gb:.1f} GB)")
    print("\nSaved: obs_datos.csv, obs_resumen.csv, obs_metadata.txt")
    print("[campaign] COMPLETADO")


if __name__ == "__main__":
    sys.exit(main())
