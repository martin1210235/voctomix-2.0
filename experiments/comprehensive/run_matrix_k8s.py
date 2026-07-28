#!/usr/bin/env python3
"""Orquestador de la MATRIZ de pruebas para el escenario KUBERNETES (k3s).

4 formatos x 5 análisis, encadenados y desatendidos, con checkpoints (no repite lo
ya válido), reintentos y un gate tras la primera celda (si hay bug sistemático, para).

Rendimiento (1.1/1.2) lo hace measure_performance_k8s.py (se autogestiona el escenario).
Latencia (2.x) y resiliencia (3.1): el orquestador levanta el escenario (k8s_scenario.sh),
verifica el mix + el formato (ffprobe), lanza el medidor y baja.

Uso: python3 run_matrix_k8s.py
"""
import csv
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMP = os.path.join(ROOT, "experiments", "comprehensive")
K8S = os.path.join(ROOT, "k8s_escenario", "experiments", "k8s_scenario.sh")
ENV = dict(os.environ, KUBECONFIG=os.environ.get("KUBECONFIG", "/etc/rancher/k3s/k3s.yaml"))

FORMATS = ["1080p25", "1080p50", "2160p25", "2160p50"]
ANALYSES = ["1-1_escalado", "1-2_sostenida", "2-1_lat_camara",
            "2-2_lat_composicion", "3-1_resiliencia"]
MAX_RETRIES = 2
AUDIT = os.path.join(ROOT, "paper", "pruebas", "matrix_k8s_stdout.log")


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    try:
        with open(AUDIT, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def sh(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                           timeout=timeout, env=ENV)
        out = (r.stdout or b"").decode(errors="replace")
        err = (r.stderr or b"").decode(errors="replace")
        return subprocess.CompletedProcess(cmd, r.returncode, out, err)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return subprocess.CompletedProcess(cmd, 124, out, f"TIMEOUT {timeout}s")


def folder_for(fmt):
    return os.path.join(ROOT, f"paper/pruebas/k8s_{fmt}")


def csv_rows(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


def validate(analysis, folder):
    rows = csv_rows(os.path.join(folder, analysis, "datos.csv"))
    if rows is None:
        return False, "datos.csv no existe"
    if analysis == "1-1_escalado":
        if len(rows) < 60:
            return False, f"pocas muestras ({len(rows)})"
        maxc = max(int(r.get("n_cameras_active", 0) or 0) for r in rows)
        if maxc < 4:
            return False, f"no 4 cámaras (máx {maxc})"
        return True, f"{len(rows)} muestras, hasta {maxc} cámaras"
    if analysis == "1-2_sostenida":
        return (len(rows) >= 150, f"{len(rows)} muestras")
    ok = sum(1 for r in rows if r.get("status") == "ok")
    return (len(rows) >= 90 and ok >= 80, f"{ok}/{len(rows)} ok")


def k8s(*args, timeout=300):
    return sh("bash " + K8S + " " + " ".join(f"'{a}'" for a in args), timeout=timeout)


def up_scenario(fmt, profile):
    """up + cams + verificación de mix y formato. Devuelve (ok, detalle)."""
    k8s("down", timeout=180)
    r = k8s("up", fmt, timeout=300)
    if "successfully rolled out" not in (r.stdout + r.stderr):
        return False, "voctocore no ready"
    k8s("cams", fmt, profile, timeout=240)
    time.sleep(20)
    # poner cam1 en fullscreen y verificar frame + formato
    k8s("select", "1", timeout=20)
    time.sleep(5)
    vf = k8s("verify-format", fmt, timeout=40)
    mf = k8s("mix-frame", "/tmp/k8s_mix_check.png", timeout=40)
    ok = "frame OK" in mf.stdout and "ANCHO/ALTO OK" in vf.stdout
    return ok, (vf.stdout.strip() + " | " + mf.stdout.strip())


def run_analysis(analysis, fmt, folder):
    out = os.path.join(folder, analysis)
    os.makedirs(os.path.join(out, "capturas"), exist_ok=True)

    if analysis == "1-1_escalado":
        return sh(f"python3 -u {COMP}/measure_performance_k8s.py escalado {out} "
                  f"--format {fmt} --idle-min 15 --step-min 15", timeout=110 * 60)
    if analysis == "1-2_sostenida":
        return sh(f"python3 -u {COMP}/measure_performance_k8s.py sostenida {out} "
                  f"--format {fmt} --duration-min 120", timeout=140 * 60)

    profile = "latency" if analysis.startswith("2-") else "experiment"
    ok, det = up_scenario(fmt, profile)
    if not ok:
        k8s("down", timeout=180)
        return subprocess.CompletedProcess("", 1, "", f"mix/formato no OK: {det}")
    if analysis == "2-1_lat_camara":
        r = sh(f"python3 -u {COMP}/measure_latency_camera.py {out} --n 100 --gap 2.5", timeout=25 * 60)
    elif analysis == "2-2_lat_composicion":
        r = sh(f"python3 -u {COMP}/measure_latency_composite.py {out} --n 100 --gap 2.5", timeout=25 * 60)
    else:
        r = sh(f"python3 -u {COMP}/measure_camera_recovery.py {out} --n 100 --gap 8 --scenario k8s", timeout=60 * 60)
    k8s("down", timeout=180)
    return r


def smoke():
    log("  SMOKE K8S: validando despliegue mínimo (voctocore + soporte + cam1 + mix)...")
    ok, det = up_scenario("1080p25", "experiment")
    k8s("down", timeout=180)
    if ok:
        log(f"  SMOKE K8S: OK ({det})")
    else:
        log(f"  SMOKE K8S: FALLO ({det})")
    return ok


def main():
    open(AUDIT, "a").close()
    log("\n" + "=" * 70)
    log("ORQUESTADOR MATRIZ — escenario KUBERNETES (k3s)")
    log("=" * 70)
    if not smoke():
        log("ABORTADO: el smoke K8s falló. No se ejecuta nada.")
        sys.exit(1)

    total_ok = total_fail = total_skip = 0
    first_cell = True
    for fmt in FORMATS:
        folder = folder_for(fmt)
        os.makedirs(folder, exist_ok=True)
        log(f"\n########## CELDA k8s · {fmt} ##########")
        cell_fail = 0
        for analysis in ANALYSES:
            if validate(analysis, folder)[0]:
                log(f"  [SKIP] {analysis} ya hecho")
                total_skip += 1
                continue
            success = False
            for attempt in range(1, MAX_RETRIES + 2):
                log(f"  [RUN ] {analysis} (intento {attempt}) ...")
                t0 = time.time()
                try:
                    r = run_analysis(analysis, fmt, folder)
                except Exception as e:
                    log(f"  [ERROR] {analysis} intento {attempt}: {e}")
                    k8s("down", timeout=180)
                    continue
                okv, detv = validate(analysis, folder)
                if okv:
                    log(f"  [OK  ] {analysis} en {int(time.time()-t0)}s — {detv}")
                    success = True
                    break
                log(f"  [FAIL] {analysis} intento {attempt}: {detv}. {(r.stderr or r.stdout or '')[-200:]}")
                k8s("down", timeout=180)
            if success:
                total_ok += 1
            else:
                log(f"  [ABANDONADA] {analysis} tras {MAX_RETRIES+1} intentos")
                total_fail += 1
                cell_fail += 1
        log(f"########## FIN CELDA k8s · {fmt} ##########")
        if first_cell and cell_fail > 0:
            log(f"GATE: la primera celda k8s tuvo {cell_fail} prueba(s) abandonada(s) "
                f"→ posible bug sistemático. Se DETIENE K8s para revisión.")
            k8s("down", timeout=180)
            return
        first_cell = False

    k8s("down", timeout=180)
    log("\n" + "=" * 70)
    log(f"MATRIZ K8S COMPLETADA. OK={total_ok} SKIP={total_skip} FALLIDAS={total_fail}")
    log("=" * 70)


if __name__ == "__main__":
    main()
