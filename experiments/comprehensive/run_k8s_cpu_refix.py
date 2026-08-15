#!/usr/bin/env python3
"""Re-measures K8s CPU/RAM (scaling + sustained, 4 formats = 8 cells) with the support
pod FIXED (all 5 sources connect). The old data was measured with an incomplete stack
(stream blanker/audio not connecting) and came out with artificially low CPU.

Writes to the OFFICIAL K8s folders, backing up the old data to _pre_supportfix/.
Checkpoints (a marker per cell), retries, logging. Meant to run under a watchdog.
"""
import csv
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMP = os.path.join(ROOT, "experiments", "comprehensive")
LOG = os.path.join(ROOT, "paper", "pruebas", "k8s_cpu_refix_log.txt")
ENV = dict(os.environ, KUBECONFIG=os.environ.get("KUBECONFIG", "/etc/rancher/k3s/k3s.yaml"))
FORMATS = ["1080p25", "1080p50", "2160p25", "2160p50"]
DONE = "K8S CPU REFIX COMPLETE"


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sh(cmd, timeout):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, timeout=timeout, env=ENV)
        return r.returncode, (r.stdout or b"").decode(errors="replace"), (r.stderr or b"").decode(errors="replace")
    except subprocess.TimeoutExpired as e:
        return 124, "", f"TIMEOUT {timeout}s"


def valid(folder, mode):
    c = os.path.join(folder, "datos.csv")
    if not os.path.isfile(c):
        return False
    try:
        rows = list(csv.DictReader(open(c, newline="")))
    except Exception:
        return False
    if mode == "escalado":
        cams = {int(r.get("n_cameras_active", -1) or -1) for r in rows}
        return len(rows) >= 60 and 4 in cams and 0 in cams
    return len(rows) >= 150


def run_cell(fmt, mode):
    sub = "1-1_escalado" if mode == "escalado" else "1-2_sostenida"
    out = os.path.join(ROOT, "paper", "pruebas", f"k8s_{fmt}", sub)
    os.makedirs(out, exist_ok=True)
    marker = os.path.join(out, "_supportfix_done")
    if os.path.isfile(marker):
        log(f"  [SKIP] {fmt} {mode} (ya re-medido con fix)")
        return True
    # backup de lo viejo una sola vez
    bak = os.path.join(out, "_pre_supportfix")
    if not os.path.isdir(bak):
        os.makedirs(bak, exist_ok=True)
        for f in ("datos.csv", "resumen.csv", "datos.xlsx"):
            if os.path.isfile(os.path.join(out, f)):
                shutil.copy(os.path.join(out, f), bak)
    for attempt in (1, 2):
        log(f"  [RUN ] {fmt} {mode} (intento {attempt})")
        sh("kubectl delete ns voctomix-exp --grace-period=0 --force", 90)
        time.sleep(3)
        if mode == "escalado":
            sh(f"python3 -u {COMP}/measure_performance_k8s.py escalado {out} "
               f"--format {fmt} --idle-min 15 --step-min 15", 110 * 60)
        else:
            sh(f"python3 -u {COMP}/measure_performance_k8s.py sostenida {out} "
               f"--format {fmt} --duration-min 120", 140 * 60)
        if valid(out, mode):
            open(marker, "w").close()
            log(f"  [OK  ] {fmt} {mode}")
            return True
        log(f"  [FAIL] {fmt} {mode} intento {attempt}")
    log(f"  [ABANDONADA] {fmt} {mode}")
    return False


def main():
    log("\n" + "=" * 70)
    log("RE-MEDICION CPU K8s con soporte arreglado (escalado + sostenida x4)")
    log("=" * 70)
    for fmt in FORMATS:
        run_cell(fmt, "escalado")
        run_cell(fmt, "sostenida")
    sh("kubectl delete ns voctomix-exp --grace-period=0 --force", 90)
    log("=" * 70)
    log(DONE)
    log("=" * 70)


if __name__ == "__main__":
    main()
