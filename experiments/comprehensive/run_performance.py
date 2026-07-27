#!/usr/bin/env python3
"""Análisis 1 (rendimiento) — driver de orquestación.

Levanta el stack (config realista BBB) y, según el modo:
  escalado  (1.1): arranca cam1, luego cam2, cam3, cam4, cada --step-min minutos.
  sostenida (1.2): arranca las 4 cámaras y las mantiene --duration-min minutos.
La telemetría registra CPU%/RAM% del host todo el tiempo en sessions/sessionN.jsonl.
Al terminar, parsea esa sesión a CSV/resumen/XLSX con parse_performance.py.

El formato de vídeo lo fija antes set_format.sh (no lo toca este driver).

Uso:
  run_performance.py escalado  <output_dir> [--step-min 15]
  run_performance.py sostenida <output_dir> [--duration-min 120]
  (opcional: --keep-up para no bajar el stack al final)
"""

import argparse
import glob
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE = ["-f", "docker-compose.yml", "-f", "docker-compose.experiment.yml"]
NONCAM = ["rabbitmq", "voctocore", "telemetry", "break", "intro",
          "stream_blanker", "audio_manager"]
CAMS = ["cam1", "cam2", "cam3", "cam4"]


def dc(*args):
    return subprocess.run(["docker", "compose", *BASE, *args],
                          cwd=ROOT, capture_output=True, text=True)


def ctrl(cmd, wait=0.5):
    """Send a voctocore control command (best-effort; only affects what is shown
    on the monitor, not the CPU/RAM measured, since every connected camera is
    processed regardless of what is displayed)."""
    try:
        s = socket.socket(); s.settimeout(2)
        s.connect(("127.0.0.1", 9999)); time.sleep(0.3)
        s.sendall((cmd + "\n").encode()); time.sleep(wait)
        s.close()
    except Exception as e:
        print(f"[perf] aviso ctrl '{cmd}': {e}")


def sessions_set():
    return set(glob.glob(os.path.join(ROOT, "sessions", "session*.jsonl")))


def wait_healthy(name, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        out = subprocess.run(["docker", "inspect", "--format",
                              "{{.State.Health.Status}}", name],
                             capture_output=True, text=True).stdout.strip()
        if out == "healthy":
            return True
        time.sleep(2)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["escalado", "sostenida"])
    ap.add_argument("output_dir")
    ap.add_argument("--step-min", type=float, default=15.0)
    ap.add_argument("--duration-min", type=float, default=120.0)
    ap.add_argument("--keep-up", action="store_true")
    args = ap.parse_args()

    print("[perf] bajando cualquier stack previo...")
    dc("down")
    time.sleep(2)
    before = sessions_set()

    print("[perf] arrancando servicios base (sin cámaras)...")
    dc("up", "-d", *NONCAM)
    if not wait_healthy("voctocore"):
        print("ERROR: voctocore no llegó a healthy", file=sys.stderr)
        sys.exit(1)
    # Esperar (hasta 30s) a que la telemetría cree su fichero de sesión.
    session = None
    for _ in range(30):
        time.sleep(1)
        new = sessions_set() - before
        if new:
            session = max(new, key=os.path.getmtime)
            break
    if session is None:
        print("ERROR: la telemetría no creó fichero de sesión (¿SAVE_LOGS=true?).",
              file=sys.stderr)
        dc("logs", "--tail", "20", "telemetry")
        sys.exit(1)
    print(f"[perf] sesión de telemetría: {os.path.basename(session)}")

    # Monitor del MIX en pantalla, solo si SHOW_GUI=1 (ejecución supervisada).
    # En ejecución autónoma NO se abre GUI (evita cuelgues y no hace falta).
    if os.environ.get("SHOW_GUI") == "1":
        try:
            subprocess.run(["bash", os.path.join(os.path.dirname(__file__), "show_gui.sh")],
                           cwd=ROOT, timeout=60)
        except Exception:
            pass

    if args.mode == "escalado":
        step = args.step_min * 60
        for cam in CAMS:
            print(f"[perf] activando {cam} (t={time.strftime('%H:%M:%S')}), midiendo {args.step_min} min...")
            dc("up", "-d", cam)
            time.sleep(8)                 # dejar que la cámara conecte
            ctrl(f"set_video_a {cam}")    # mostrarla en el monitor (no afecta a la medida)
            time.sleep(max(0, step - 8))
    else:  # sostenida
        print("[perf] activando las 4 cámaras...")
        dc("up", "-d", *CAMS)
        time.sleep(8)
        ctrl("set_video_a cam1")
        print(f"[perf] carga sostenida {args.duration_min} min (t={time.strftime('%H:%M:%S')})...")
        time.sleep(args.duration_min * 60)

    print("[perf] fin de la ventana de medida.")
    # Buscar la sesión final (por si el índice cambió)
    if session is None:
        after = sessions_set() - before
        session = max(after, key=os.path.getmtime) if after else None
    if session is None:
        print("ERROR: no se encontró la sesión de telemetría.", file=sys.stderr)
        sys.exit(1)

    if not args.keep_up:
        print("[perf] bajando el stack...")
        dc("down")

    label = args.mode
    print(f"[perf] parseando {os.path.basename(session)} -> {args.output_dir}")
    subprocess.run([sys.executable,
                    os.path.join(os.path.dirname(__file__), "parse_performance.py"),
                    session, args.output_dir, "--label", label])


if __name__ == "__main__":
    main()
