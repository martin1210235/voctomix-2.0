#!/usr/bin/env python3
"""Autonomous test-matrix orchestrator — DOCKER scenario x 4 formats.

Runs, in order, the 5 tests for each cell (1.1, 1.2, 2.1, 2.2, 3.1) for
1080p25, 1080p50, 2160p25, 2160p50. For each test:
  - skips it if already done (checkpoint = datos.csv exists),
  - runs it with the correct config (BBB for 1 and 3, solid colour for 2) and
    the monitor/GUI on screen,
  - VALIDATES the result (row count, consistency),
  - if it fails, cleans up and RETRIES up to 2 times; if it still fails, logs it
    and continues (does not abort the matrix).
Logs everything to paper/pruebas/AUDIT_MATRIX.md with timestamps (heartbeat).
STOPS once Docker is done (does not touch Local or Kubernetes).

Designed for unattended execution. Usage:  python3 run_matrix.py
"""

import csv
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMP = "experiments/comprehensive"
AUDIT = os.path.join(ROOT, "paper/pruebas/AUDIT_MATRIX.md")
os.environ.setdefault("DISPLAY", ":0")

SCENARIOS = ["docker"]                       # Local/K8s: pending (tooling/installation)
FORMATS = ["1080p25", "1080p50", "2160p25", "2160p50"]
ANALYSES = ["1-1_escalado", "1-2_sostenida", "2-1_lat_camara",
            "2-2_lat_composicion", "3-1_resiliencia"]
MAX_RETRIES = 2


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sh(cmd, timeout=600):
    """Runs a shell command with a timeout ALWAYS (no call is allowed to
    hang indefinitely). Long measurements pass their own larger timeout."""
    try:
        return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(cmd, 124, e.stdout or "", f"TIMEOUT after {timeout}s")


def folder_for(scenario, fmt):
    if scenario == "docker" and fmt == "1080p25":
        return os.path.join(ROOT, "paper/pruebas/docker_1080p25")
    return os.path.join(ROOT, f"paper/pruebas/{scenario}_{fmt}")


def down_all():
    sh("docker compose -f docker-compose.yml -f docker-compose.experiment.yml down", timeout=120)
    sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml down", timeout=120)
    sh("pkill -f 'gst-launch.*port=11000'", timeout=20)
    sh("pkill -f 'python3 voctogui.py'", timeout=20)
    time.sleep(6)


def up(config):
    """config: 'experiment' (BBB) or 'latency' (solid colour). Waits up to 150s
    for all 4 cameras to become healthy."""
    sh(f"docker compose -f docker-compose.yml -f docker-compose.{config}.yml up -d", timeout=180)
    end = time.time() + 150
    while time.time() < end:
        r = sh("docker ps --format '{{.Names}} {{.Status}}' | grep -cE '^cam[0-9] Up.*healthy'", timeout=20)
        try:
            if int(r.stdout.strip()) >= 4:
                time.sleep(5)
                return True
        except ValueError:
            pass
        time.sleep(4)
    return False


def csv_rows(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


def validate(analysis, folder):
    """Returns (ok, detail)."""
    path = os.path.join(folder, analysis, "datos.csv")
    rows = csv_rows(path)
    if rows is None:
        return False, "datos.csv does not exist or is unreadable"
    if analysis == "1-1_escalado":
        if len(rows) < 60:
            return False, f"too few samples ({len(rows)})"
        maxc = max(int(r.get("n_cameras_active", 0) or 0) for r in rows)
        if maxc < 4:
            return False, f"4 cameras were not activated (max {maxc})"
        return True, f"{len(rows)} samples, up to {maxc} cameras"
    if analysis == "1-2_sostenida":
        if len(rows) < 150:
            return False, f"too few samples ({len(rows)})"
        return True, f"{len(rows)} samples"
    # latency / resilience: 100 iterations with status
    ok = sum(1 for r in rows if r.get("status") == "ok")
    if len(rows) < 90 or ok < 80:
        return False, f"{ok}/{len(rows)} ok"
    return True, f"{ok}/{len(rows)} ok"


# ---- per-test runners (no GUI; each one leaves the environment clean before starting) ----
def _save_log(out, r):
    try:
        with open(os.path.join(out, "run.log"), "w", encoding="utf-8") as f:
            f.write((r.stdout or "") + "\n---STDERR---\n" + (r.stderr or ""))
    except Exception:
        pass
    return r


def run_analysis(analysis, scenario, fmt, folder):
    out = os.path.join(folder, analysis)
    os.makedirs(os.path.join(out, "capturas"), exist_ok=True)
    sh(f"bash {COMP}/set_format.sh {fmt}", timeout=60)

    if analysis == "1-1_escalado":
        down_all()
        return _save_log(out, sh(
            f"python3 -u {COMP}/run_performance.py escalado {out} --step-min 15",
            timeout=80 * 60))
    if analysis == "1-2_sostenida":
        down_all()
        return _save_log(out, sh(
            f"python3 -u {COMP}/run_performance.py sostenida {out} --duration-min 120",
            timeout=140 * 60))
    if analysis == "2-1_lat_camara":
        down_all()
        if not up("latency"):
            return subprocess.CompletedProcess("", 1, "", "cameras did not connect (latency)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_latency_camera.py {out} --n 100 --gap 2.5",
            timeout=25 * 60))
    if analysis == "2-2_lat_composicion":
        down_all()
        if not up("latency"):
            return subprocess.CompletedProcess("", 1, "", "cameras did not connect (latency)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_latency_composite.py {out} --n 100 --gap 2.5",
            timeout=25 * 60))
    if analysis == "3-1_resiliencia":
        down_all()
        if not up("experiment"):
            return subprocess.CompletedProcess("", 1, "", "cameras did not connect (experiment)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_camera_recovery.py {out} --n 100 --gap 8",
            timeout=60 * 60))
    return subprocess.CompletedProcess("", 1, "", "unknown test")


def smoke_2160p50():
    log("  SMOKE TEST 2160p50: checking whether the system saturates with 4 cameras at 4K50...")
    sh(f"bash {COMP}/set_format.sh 2160p50")
    down_all()
    ok = up("experiment")
    time.sleep(20)
    r = sh("docker ps --format '{{.Names}} {{.Status}}' | grep -cE '^cam[0-9] Up.*healthy'")
    cams = r.stdout.strip()
    # approximate host CPU
    cpu = sh("grep 'cpu ' /proc/stat")
    down_all()
    log(f"  SMOKE 2160p50: cameras connected={cams}, startup={'OK' if ok else 'FAILED'}. "
        f"(If it saturates, the measurements will reflect it as a performance ceiling.)")


def main():
    log("=" * 70)
    log("MATRIX ORCHESTRATOR — start (Docker scenario, 4 formats)")
    log(f"Formats: {FORMATS} · Tests per cell: {ANALYSES}")
    log("Stops once Docker is done (Local and Kubernetes: manual).")
    log("=" * 70)

    total_ok = total_fail = total_skip = 0
    for scenario in SCENARIOS:
        for fmt in FORMATS:
            folder = folder_for(scenario, fmt)
            os.makedirs(folder, exist_ok=True)
            log(f"\n########## CELL {scenario} · {fmt} ##########")
            if fmt == "2160p50":
                try:
                    smoke_2160p50()
                except Exception as e:
                    log(f"  smoke warning: {e}")
            for analysis in ANALYSES:
                ok_ckpt, det = validate(analysis, folder)
                if ok_ckpt:
                    log(f"  [SKIP] {analysis} already done ({det})")
                    total_skip += 1
                    continue
                success = False
                for attempt in range(1, MAX_RETRIES + 2):
                    log(f"  [RUN ] {analysis} (attempt {attempt}) ...")
                    t0 = time.time()
                    try:
                        r = run_analysis(analysis, scenario, fmt, folder)
                    except subprocess.TimeoutExpired:
                        log(f"  [TIMEOUT] {analysis} attempt {attempt}")
                        down_all()
                        continue
                    except Exception as e:
                        log(f"  [ERROR] {analysis} attempt {attempt}: {e}")
                        down_all()
                        continue
                    dur = int(time.time() - t0)
                    okv, detv = validate(analysis, folder)
                    if okv:
                        log(f"  [OK  ] {analysis} in {dur}s — {detv}")
                        success = True
                        break
                    else:
                        tail = (r.stderr or r.stdout or "")[-300:]
                        log(f"  [FAIL] {analysis} attempt {attempt} ({dur}s): {detv}. {tail}")
                        down_all()
                if success:
                    total_ok += 1
                else:
                    log(f"  [ABANDONED] {analysis} after {MAX_RETRIES+1} attempts — continuing")
                    total_fail += 1
            log(f"########## END CELL {scenario} · {fmt} ##########")

    down_all()
    log("\n" + "=" * 70)
    log(f"DOCKER MATRIX COMPLETE. OK={total_ok} SKIP={total_skip} FAILED={total_fail}")
    log("Local and Kubernetes: pending (manual, with you present).")
    log("=" * 70)


if __name__ == "__main__":
    main()
