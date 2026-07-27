#!/usr/bin/env python3
"""Análisis 2.2 — latencia de vídeo de conmutación de composición (fs <-> sbs).

Alterna entre pantalla completa (fs) y side-by-side (sbs) con `cut`, y mide el
tiempo hasta que la salida del mix (puerto 11000) refleja el nuevo modo. Señal:
el punto centro-derecha muestra la fuente A en fs y la fuente B en sbs.

  fs->sbs: latencia = t(primer frame con B a la derecha) - t(comando)
  sbs->fs: latencia = t(primer frame con A a la derecha) - t(comando)

Requiere el stack con la config de latencia (colores sólidos, cam1=rojo A,
cam2=verde B). Salidas: datos.csv, resumen.csv, datos.xlsx.

Uso:
  measure_latency_composite.py <output_dir> [--n 100] [--gap 2.5]
"""

import argparse
import os
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_video import MixCornerReader, classify  # noqa: E402
from lib_common import stats, write_csv, write_summary_csv, bundle_xlsx  # noqa: E402

SRC_A = "cam1"   # rojo, izquierda en sbs
SRC_B = "cam2"   # verde, derecha en sbs


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--gap", type=float, default=2.5)
    ap.add_argument("--ctrl-port", type=int, default=9999)
    ap.add_argument("--mix-port", type=int, default=11000)
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()

    s = socket.socket()
    s.settimeout(2.0)
    s.connect(("127.0.0.1", args.ctrl_port))
    time.sleep(0.4)
    send(s, "")
    send(s, f"cut fs({SRC_A},{SRC_B})")

    # Right-centre region: shows A in fs, B in sbs.
    reader = MixCornerReader(args.mix_port, w=120, h=120, x="iw*0.75-60", y="ih*0.5-60")
    time.sleep(2.0)
    if not reader.alive():
        print("ERROR: no se pudo abrir el lector del mix (puerto 11000).", file=sys.stderr)
        sys.exit(1)

    mode = "fs"
    rows = []
    print(f"Midiendo {args.n} conmutaciones de composición (fs<->sbs, corte)...")
    for i in range(args.n):
        if mode == "fs":
            target_mode, cmd, expect = "sbs", f"cut sbs({SRC_A},{SRC_B})", SRC_B
        else:
            target_mode, cmd, expect = "fs", f"cut fs({SRC_A},{SRC_B})", SRC_A
        t0 = time.monotonic()
        send(s, cmd, wait=0.0)
        det = reader.wait_until(lambda c: c == expect, after_t=t0, timeout=args.timeout)
        if det is None:
            rows.append({"iteration": i + 1, "from": mode, "to": target_mode,
                         "latency_ms": None, "status": "timeout"})
            print(f"  [{i+1:3d}] {mode}->{target_mode}  TIMEOUT")
        else:
            lat = round((det[0] - t0) * 1000, 1)
            rows.append({"iteration": i + 1, "from": mode, "to": target_mode,
                         "latency_ms": lat, "status": "ok"})
            print(f"  [{i+1:3d}] {mode}->{target_mode}  {lat} ms")
        mode = target_mode
        time.sleep(args.gap)

    s.close()
    reader.stop()

    fields = ["iteration", "from", "to", "latency_ms", "status"]
    lat = [r["latency_ms"] for r in rows if r["status"] == "ok"]
    summary = [{"metric": "latency_ms", **stats(lat)},
               {"metric": "n_ok", "n": len(lat)},
               {"metric": "n_timeout", "n": sum(1 for r in rows if r["status"] == "timeout")}]
    sfields = ["metric", "n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std"]

    os.makedirs(args.output_dir, exist_ok=True)
    write_csv(os.path.join(args.output_dir, "datos.csv"), fields, rows)
    write_summary_csv(os.path.join(args.output_dir, "resumen.csv"), summary)
    bundle_xlsx(os.path.join(args.output_dir, "datos.xlsx"),
                {"datos": (fields, rows), "resumen": (sfields, summary)})

    st = stats(lat)
    print(f"\nOK: {len(lat)}/{args.n}  mediana={st['median']} ms  p95={st['p95']} ms  "
          f"min={st['min']} max={st['max']}")
    print(f"  → {args.output_dir}/datos.csv , resumen.csv , datos.xlsx")


if __name__ == "__main__":
    main()
