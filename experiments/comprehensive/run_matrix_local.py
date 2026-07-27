#!/usr/bin/env python3
"""Orquestador del escenario LOCAL (nativo) — 4 formatos × 5 pruebas.

Se ejecuta DESPUÉS de Docker (los puertos deben estar libres). Empieza con un
SMOKE TEST que valida el arranque nativo (voctocore + 1 cámara + mix). Si el smoke
falla, aborta sin ejecutar nada (no produce basura). Si la PRIMERA celda completa
tiene alguna prueba abandonada (bug sistemático), también se detiene para revisión.
Reutiliza los medidores (agnósticos al escenario) y measure_performance_local /
local_scenario.sh para lo nativo. Checkpoints, reintentos, timeouts y auditoría.

Uso:  python3 run_matrix_local.py
"""

import csv
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMP = "experiments/comprehensive"
LOCAL = os.path.join(ROOT, COMP, "local_scenario.sh")
AUDIT = os.path.join(ROOT, "paper/pruebas/AUDIT_MATRIX.md")

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
    try:
        return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        if isinstance(out, (bytes, bytearray)):
            out = out.decode(errors="replace")
        return subprocess.CompletedProcess(cmd, 124, out or "", f"TIMEOUT {timeout}s")


def local(cmd_args, timeout=180):
    """Ejecuta local_scenario.sh SIN capturar por pipe (redirige a fichero), para
    que subprocess vuelva al terminar el script y NO espere a los procesos de fondo
    (voctocore/ffmpeg) que heredarían el pipe y colgarían la llamada."""
    logf = "/tmp/local_scn.log"
    try:
        with open(logf, "w") as f:
            subprocess.run(f"bash {LOCAL} {cmd_args}", shell=True, cwd=ROOT,
                           stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    try:
        out = open(logf, encoding="utf-8", errors="replace").read()
    except Exception:
        out = ""
    return subprocess.CompletedProcess(cmd_args, 0, out, "")


def folder_for(fmt):
    return os.path.join(ROOT, f"paper/pruebas/local_{fmt}")


def csv_rows(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
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


def up_cams_native(cfg):
    """base_up + 4 cámaras nativas + espera a que el mix produzca vídeo."""
    local("down")
    r = local("base_up", timeout=180)
    if "base_up OK" not in (r.stdout or ""):
        return False
    for n in (1, 2, 3, 4):
        local(f"cam_up {n} {cfg}")
    time.sleep(40)
    # verificar que el mix produce un frame
    g = sh("timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 "
           "-vf 'select=gte(t\\,1)' -frames:v 1 /tmp/local_mix.png", timeout=30)
    return os.path.isfile("/tmp/local_mix.png") and os.path.getsize("/tmp/local_mix.png") > 1000


def _save_log(out, r):
    try:
        with open(os.path.join(out, "run.log"), "w", encoding="utf-8") as f:
            f.write((r.stdout or "") + "\n---STDERR---\n" + (r.stderr or ""))
    except Exception:
        pass
    return r


def run_analysis(analysis, fmt, folder):
    out = os.path.join(folder, analysis)
    os.makedirs(os.path.join(out, "capturas"), exist_ok=True)
    sh(f"bash {COMP}/set_format.sh {fmt}", timeout=60)

    if analysis == "1-1_escalado":
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_performance_local.py escalado {out} --step-min 15",
            timeout=80 * 60))
    if analysis == "1-2_sostenida":
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_performance_local.py sostenida {out} --duration-min 120",
            timeout=140 * 60))
    if analysis == "2-1_lat_camara":
        if not up_cams_native("latency"):
            return subprocess.CompletedProcess("", 1, "", "mix nativo sin vídeo (latency)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_latency_camera.py {out} --n 100 --gap 2.5", timeout=25 * 60))
    if analysis == "2-2_lat_composicion":
        if not up_cams_native("latency"):
            return subprocess.CompletedProcess("", 1, "", "mix nativo sin vídeo (latency)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_latency_composite.py {out} --n 100 --gap 2.5", timeout=25 * 60))
    if analysis == "3-1_resiliencia":
        if not up_cams_native("experiment"):
            return subprocess.CompletedProcess("", 1, "", "mix nativo sin vídeo (experiment)")
        return _save_log(out, sh(
            f"python3 -u {COMP}/measure_camera_recovery.py {out} --n 100 --gap 8 --scenario local",
            timeout=60 * 60))
    return subprocess.CompletedProcess("", 1, "", "prueba desconocida")


def smoke():
    log("  SMOKE LOCAL: validando arranque nativo (voctocore + 1 cámara + mix)...")
    sh(f"bash {COMP}/set_format.sh 1080p25", timeout=60)
    local("down")
    r = local("base_up", timeout=180)
    if "base_up OK" not in (r.stdout or ""):
        log(f"  SMOKE FALLO: voctocore nativo no arrancó. {r.stdout} {r.stderr}")
        local("down")
        return False
    local("cam_up 1 latency")
    time.sleep(25)
    g = sh("timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 "
           "-vf 'select=gte(t\\,1)' -frames:v 1 /tmp/local_smoke.png", timeout=30)
    ok = os.path.isfile("/tmp/local_smoke.png") and os.path.getsize("/tmp/local_smoke.png") > 1000
    local("down")
    log(f"  SMOKE LOCAL: {'OK (mix nativo produce vídeo)' if ok else 'FALLO (mix sin vídeo)'}")
    return ok


def main():
    log("\n" + "=" * 70)
    log("ORQUESTADOR MATRIZ — escenario LOCAL (nativo)")
    log("=" * 70)
    if not smoke():
        log("LOCAL abortado: el smoke test nativo falló. Requiere revisión manual.")
        return

    total_ok = total_fail = total_skip = 0
    first_cell = True
    for fmt in FORMATS:
        folder = folder_for(fmt)
        os.makedirs(folder, exist_ok=True)
        log(f"\n########## CELDA local · {fmt} ##########")
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
                    local("down")
                    continue
                okv, detv = validate(analysis, folder)
                if okv:
                    log(f"  [OK  ] {analysis} en {int(time.time()-t0)}s — {detv}")
                    success = True
                    break
                log(f"  [FAIL] {analysis} intento {attempt}: {detv}. {(r.stderr or r.stdout or '')[-200:]}")
                local("down")
            if success:
                total_ok += 1
            else:
                log(f"  [ABANDONADA] {analysis} tras {MAX_RETRIES+1} intentos")
                total_fail += 1
                cell_fail += 1
        log(f"########## FIN CELDA local · {fmt} ##########")
        if first_cell and cell_fail > 0:
            log(f"GATE: la primera celda local tuvo {cell_fail} prueba(s) abandonada(s) "
                f"→ posible bug sistemático. Se DETIENE Local para revisión (no se malgastan horas).")
            local("down")
            return
        first_cell = False

    local("down")
    log("\n" + "=" * 70)
    log(f"MATRIZ LOCAL COMPLETADA. OK={total_ok} SKIP={total_skip} FALLIDAS={total_fail}")
    log("=" * 70)


if __name__ == "__main__":
    main()
