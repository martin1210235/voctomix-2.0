#!/usr/bin/env python3
"""Análisis 3.1 — resiliencia: caída de una cámara y tiempo de recuperación.

Con la cámara víctima en pantalla completa, simula una caída realista matando
su proceso ffmpeg dentro del contenedor (`docker exec camN pkill -9 ffmpeg`).
La política de restart de Docker reinicia el contenedor automáticamente; se mide
el tiempo hasta que el feed de la víctima vuelve a verse en la salida del mix.

Por iteración se registran:
  detect_ms  = t(esquina deja de mostrar la víctima)   - t(crash)   [detección]
  restore_ms = t(esquina vuelve a mostrar la víctima)   - t(detección) [restablecimiento]
  mttr_ms    = t(feed restaurado)                        - t(crash)   [recuperación total]

Pensado para la config realista (BBB + marcadores). Rota la víctima cam1..cam4.
Salidas: datos.csv, resumen.csv, datos.xlsx.

Uso:
  measure_camera_recovery.py <output_dir> [--n 100] [--gap 8]
"""

import argparse
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_video import MixCornerReader, classify  # noqa: E402
from lib_common import stats, write_csv, write_summary_csv, bundle_xlsx  # noqa: E402

CYCLE = ["cam1", "cam2", "cam3", "cam4"]


def send(sock, cmd, wait=0.3):
    sock.sendall((cmd + "\n").encode())
    time.sleep(wait)
    sock.setblocking(False)
    try:
        while sock.recv(8192):
            pass
    except (BlockingIOError, OSError):
        pass
    sock.setblocking(True)


def wait_color(reader, want_equal, target, after_t, timeout):
    """Wait until classify(corner) is (or is not) target. Returns time or None."""
    if want_equal:
        res = reader.wait_until(lambda c: c == target, after_t, timeout)
    else:
        res = reader.wait_until(lambda c: c != target, after_t, timeout)
    return res[0] if res else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--gap", type=float, default=8.0, help="estabilización entre iteraciones (s)")
    ap.add_argument("--ctrl-port", type=int, default=9999)
    ap.add_argument("--mix-port", type=int, default=11000)
    ap.add_argument("--loss-timeout", type=float, default=10.0)
    ap.add_argument("--recover-timeout", type=float, default=40.0)
    ap.add_argument("--scenario", default="docker", choices=["docker", "local"],
                    help="docker: crash vía docker exec; local: crash del ffmpeg nativo")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))

    def crash(victim):
        if args.scenario == "local":
            subprocess.run(["bash", os.path.join(here, "local_scenario.sh"), "crash", victim[-1]],
                           capture_output=True)
        else:
            subprocess.run(["docker", "exec", victim, "pkill", "-9", "ffmpeg"],
                           capture_output=True)

    s = socket.socket()
    s.settimeout(2.0)
    s.connect(("127.0.0.1", args.ctrl_port))
    time.sleep(0.4)
    send(s, "")

    reader = MixCornerReader(args.mix_port)
    time.sleep(2.0)
    if not reader.alive():
        print("ERROR: no se pudo abrir el lector del mix (puerto 11000).", file=sys.stderr)
        sys.exit(1)

    rows = []
    print(f"Midiendo {args.n} caídas de cámara y recuperación...")
    for i in range(args.n):
        victim = CYCLE[i % 4]
        other = CYCLE[(i + 1) % 4]
        # Poner la víctima en pantalla completa y confirmar que se ve.
        send(s, f"cut fs({victim},{other})")
        ready = reader.wait_until(lambda c: c == victim, time.monotonic(), timeout=8.0)
        if ready is None:
            rows.append({"iteration": i + 1, "victim": victim, "detect_ms": None,
                         "restore_ms": None, "mttr_ms": None, "status": "not_ready"})
            print(f"  [{i+1:3d}] {victim}  NO LISTA (se salta)")
            time.sleep(2)
            continue
        time.sleep(1.0)

        t0 = time.monotonic()
        crash(victim)
        t_down = wait_color(reader, False, victim, t0, args.loss_timeout)
        if t_down is None:
            rows.append({"iteration": i + 1, "victim": victim, "detect_ms": None,
                         "restore_ms": None, "mttr_ms": None, "status": "no_loss"})
            print(f"  [{i+1:3d}] {victim}  no se detectó pérdida")
            time.sleep(args.gap)
            continue
        t_rec = wait_color(reader, True, victim, t_down, args.recover_timeout)
        if t_rec is None:
            rows.append({"iteration": i + 1, "victim": victim,
                         "detect_ms": round((t_down - t0) * 1000, 1),
                         "restore_ms": None, "mttr_ms": None, "status": "no_recovery"})
            print(f"  [{i+1:3d}] {victim}  NO RECUPERADA (>{args.recover_timeout}s)")
            time.sleep(args.gap)
            continue

        detect = round((t_down - t0) * 1000, 1)
        restore = round((t_rec - t_down) * 1000, 1)
        mttr = round((t_rec - t0) * 1000, 1)
        rows.append({"iteration": i + 1, "victim": victim, "detect_ms": detect,
                     "restore_ms": restore, "mttr_ms": mttr, "status": "ok"})
        print(f"  [{i+1:3d}] {victim}  detect={detect}ms  restore={restore}ms  MTTR={mttr}ms")
        time.sleep(args.gap)

    s.close()
    reader.stop()

    fields = ["iteration", "victim", "detect_ms", "restore_ms", "mttr_ms", "status"]
    mttr = [r["mttr_ms"] for r in rows if r["status"] == "ok"]
    summary = [{"metric": "mttr_ms", **stats(mttr)},
               {"metric": "detect_ms", **stats([r["detect_ms"] for r in rows if r["status"] == "ok"])},
               {"metric": "restore_ms", **stats([r["restore_ms"] for r in rows if r["status"] == "ok"])},
               {"metric": "n_ok", "n": len(mttr)},
               {"metric": "n_fail", "n": sum(1 for r in rows if r["status"] != "ok")}]
    sfields = ["metric", "n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std"]

    os.makedirs(args.output_dir, exist_ok=True)
    write_csv(os.path.join(args.output_dir, "datos.csv"), fields, rows)
    write_summary_csv(os.path.join(args.output_dir, "resumen.csv"), summary)
    bundle_xlsx(os.path.join(args.output_dir, "datos.xlsx"),
                {"datos": (fields, rows), "resumen": (sfields, summary)})

    st = stats(mttr)
    print(f"\nOK: {len(mttr)}/{args.n}  MTTR mediana={st['median']} ms  p95={st['p95']} ms  "
          f"min={st['min']} max={st['max']}")
    print(f"  → {args.output_dir}/datos.csv , resumen.csv , datos.xlsx")


if __name__ == "__main__":
    main()
