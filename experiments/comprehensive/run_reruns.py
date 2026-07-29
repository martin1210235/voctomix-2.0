#!/usr/bin/env python3
"""Orquestador de RE-EJECUCIONES para el viaje. Corre solo, secuencial y robusto.

Hace, en orden:
  1) ESCALADOS de los 3 escenarios (docker, local, k8s) x 4 formatos, con baseline de
     0 cámaras (15 min) + 4 pasos de 15 min. Se agrupan por FORMATO (docker/local/k8s
     seguidos) para que la CPU se mida en condiciones lo más parecidas posible → resuelve
     la incongruencia de CPU entre escenarios. Salida a paper/pruebas/reruns/.
  2) LATENCIA 2.2 de Docker 2160p50 x3 (caracterizar la inestabilidad del outlier).
  3) SOSTENIDA de 24 h de Docker 2160p50 (memory-leak).

Limpieza cruzada total antes de cada prueba, checkpoints (no repite lo válido), reintentos.
NO sobrescribe los datos oficiales: escribe a carpetas nuevas para comparar y decidir después.

Uso:
  python3 run_reruns.py                 # real (idle 15, step 15, sostenida 1440 min)
  python3 run_reruns.py --quick         # validación rápida (idle 0.4, step 0.4, sost 2 min)
"""
import argparse
import csv
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMP = os.path.join(ROOT, "experiments", "comprehensive")
K8SDIR = os.path.join(ROOT, "k8s_escenario", "experiments")
OUTBASE = os.path.join(ROOT, "paper", "pruebas", "reruns")
LOG = os.path.join(OUTBASE, "rerun_log.txt")
ENV = dict(os.environ, KUBECONFIG=os.environ.get("KUBECONFIG", "/etc/rancher/k3s/k3s.yaml"))

FORMATS = ["1080p25", "1080p50", "2160p25", "2160p50"]
SCENARIOS = ["docker", "local", "k8s"]
MAX_RETRIES = 1  # 2 intentos totales


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    os.makedirs(OUTBASE, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sh(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                           timeout=timeout, env=ENV)
        return r.returncode, (r.stdout or b"").decode(errors="replace"), (r.stderr or b"").decode(errors="replace")
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return 124, out, f"TIMEOUT {timeout}s"


def full_cleanup():
    """Deja la máquina limpia: baja docker, local y k8s, y espera a que 9999 quede libre."""
    sh("docker compose -f docker-compose.yml -f docker-compose.experiment.yml down --remove-orphans", 150)
    sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml down --remove-orphans", 150)
    sh(f"bash {COMP}/local_scenario.sh down", 90)
    sh("kubectl delete ns voctomix-exp --grace-period=0 --force", 90)
    for _ in range(40):
        rc, out, _ = sh("ss -lnt | grep -q ':9999' && echo BUSY || echo FREE", 10)
        if "FREE" in out:
            break
        time.sleep(2)


def esc_valid(folder):
    csvf = os.path.join(folder, "datos.csv")
    if not os.path.isfile(csvf):
        return False
    try:
        with open(csvf, newline="") as f:
            rows = list(csv.DictReader(f))
    except Exception:
        return False
    if len(rows) < 60:
        return False
    maxc = max(int(r.get("n_cameras_active", 0) or 0) for r in rows)
    cams = {int(r.get("n_cameras_active", 0) or 0) for r in rows}
    return maxc >= 4 and 0 in cams  # llegó a 4 cámaras y tiene baseline 0


def run_escalado(scenario, fmt, idle, step):
    out = os.path.join(OUTBASE, f"{scenario}_{fmt}", "1-1_escalado")
    os.makedirs(out, exist_ok=True)
    if esc_valid(out):
        log(f"  [SKIP] escalado {scenario} {fmt} (ya válido)")
        return True
    for attempt in range(1, MAX_RETRIES + 2):
        log(f"  [RUN ] escalado {scenario} {fmt} (intento {attempt})")
        full_cleanup()
        if scenario in ("docker", "local"):
            sh(f"bash {COMP}/set_format.sh {fmt}", 60)
        if scenario == "docker":
            rc, o, e = sh(f"python3 -u {COMP}/run_performance.py escalado {out} "
                          f"--idle-min {idle} --step-min {step}", timeout=int((idle + 4 * step + 20) * 60))
        elif scenario == "local":
            rc, o, e = sh(f"python3 -u {COMP}/measure_performance_local.py escalado {out} "
                          f"--idle-min {idle} --step-min {step}", timeout=int((idle + 4 * step + 20) * 60))
        else:  # k8s
            rc, o, e = sh(f"python3 -u {COMP}/measure_performance_k8s.py escalado {out} "
                          f"--format {fmt} --idle-min {idle} --step-min {step}", timeout=int((idle + 4 * step + 20) * 60))
        if esc_valid(out):
            log(f"  [OK  ] escalado {scenario} {fmt}")
            return True
        log(f"  [FAIL] escalado {scenario} {fmt}: {(e or o)[-200:]}")
    log(f"  [ABANDONADA] escalado {scenario} {fmt}")
    return False


def ffprobe_capture(scenario, fmt):
    """Best-effort: levanta el stack (color sólido), ffprobe del mix, guarda evidencia, baja.
    Completa la verificación de formato pendiente de Docker/Local (K8s ya la hace)."""
    evid = os.path.join(ROOT, "paper", "pruebas", "verificacion_formatos")
    os.makedirs(evid, exist_ok=True)
    full_cleanup()
    sh(f"bash {COMP}/set_format.sh {fmt}", 60)
    if scenario == "docker":
        sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml up -d", 200)
        time.sleep(55)
    else:
        sh(f"bash {COMP}/local_scenario.sh base_up", 150)
        for n in (1, 2, 3, 4):
            sh(f"bash {COMP}/local_scenario.sh cam_up {n} latency", 30)
        time.sleep(35)
    sh(f"{{ echo '=== '$(date '+%F %T')' | {scenario} | {fmt} ==='; "
       f"timeout 20 ffprobe -v error -select_streams v:0 "
       f"-show_entries stream=width,height,r_frame_rate,avg_frame_rate "
       f"-of default=noprint_wrappers=1 tcp://127.0.0.1:11000; echo; }} "
       f">> {evid}/ffprobe_{scenario}_{fmt}.txt 2>/dev/null", 30)
    sh(f"timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 "
       f"-vf 'select=gte(t\\,1)' -frames:v 1 {evid}/frame_{scenario}_{fmt}.png 2>/dev/null", 30)
    if scenario == "docker":
        sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml down --remove-orphans", 150)
    else:
        sh(f"bash {COMP}/local_scenario.sh down", 60)
    log(f"  [ffprobe] {scenario} {fmt} capturado")


def run_docker_latency_4k50(n, gap):
    out = os.path.join(OUTBASE, "docker_2160p50_lat22", f"run{n}")
    os.makedirs(out, exist_ok=True)
    if os.path.isfile(os.path.join(out, "datos.csv")):
        log(f"  [SKIP] lat22 docker 2160p50 run{n}")
        return
    log(f"  [RUN ] lat22 docker 2160p50 run{n}")
    full_cleanup()
    sh(f"bash {COMP}/set_format.sh 2160p50", 60)
    sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml up -d", 200)
    time.sleep(55)
    sh(f"python3 -u {COMP}/measure_latency_composite.py {out} --n 100 --gap {gap}", timeout=25 * 60)
    sh("docker compose -f docker-compose.yml -f docker-compose.latency.yml down --remove-orphans", 150)


def run_sostenida_24h(minutes):
    out = os.path.join(OUTBASE, "docker_2160p50_sostenida24h")
    os.makedirs(out, exist_ok=True)
    if os.path.isfile(os.path.join(out, "datos.csv")):
        log("  [SKIP] sostenida 24h docker 2160p50")
        return
    log(f"  [RUN ] sostenida {minutes} min docker 2160p50")
    full_cleanup()
    sh(f"bash {COMP}/set_format.sh 2160p50", 60)
    sh(f"python3 -u {COMP}/run_performance.py sostenida {out} --duration-min {minutes}",
       timeout=int((minutes + 30) * 60))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    idle = 0.4 if args.quick else 15.0
    step = 0.4 if args.quick else 15.0
    sost = 2.0 if args.quick else 1440.0
    gap = 1.0 if args.quick else 2.5

    os.makedirs(OUTBASE, exist_ok=True)
    log("\n" + "=" * 70)
    log(f"ORQUESTADOR DE RE-EJECUCIONES {'(QUICK)' if args.quick else '(REAL)'}")
    log("=" * 70)

    log("### FASE 1: escalados de los 3 escenarios (agrupados por formato) ###")
    for fmt in FORMATS:
        for sc in SCENARIOS:
            run_escalado(sc, fmt, idle, step)

    log("### FASE 2: verificacion ffprobe de formato Docker/Local (K8s ya verificado) ###")
    for sc in ("docker", "local"):
        for fmt in FORMATS:
            try:
                ffprobe_capture(sc, fmt)
            except Exception as e:
                log(f"  [ffprobe {sc} {fmt}] error (no bloqueante): {e}")

    log("### FASE 3: latencia 2.2 Docker 2160p50 x3 (caracterizar inestabilidad) ###")
    for n in (1, 2, 3):
        run_docker_latency_4k50(n, gap)

    log("### FASE 4: sostenida 24h Docker 2160p50 (leak) ###")
    run_sostenida_24h(sost)

    full_cleanup()
    log("=" * 70)
    log("RE-EJECUCIONES COMPLETADAS")
    log("=" * 70)


if __name__ == "__main__":
    main()
