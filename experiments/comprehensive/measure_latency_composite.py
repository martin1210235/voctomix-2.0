#!/usr/bin/env python3
"""Analysis 2.2 — composite-switching video latency (fs <-> sbs).

Alternates between fullscreen (fs) and side-by-side (sbs) with `cut`, and
measures the time until the mix output (port 11000) reflects the new mode.
Signal: the centre-right point shows source A in fs and source B in sbs.

  fs->sbs: latency = t(first frame with B on the right) - t(command)
  sbs->fs: latency = t(first frame with A on the right) - t(command)

Requires the stack with the latency config (solid colours, cam1=red A,
cam2=green B). Outputs: datos.csv, resumen.csv, datos.xlsx.

Usage:
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

SRC_A = "cam1"   # red, left in sbs
SRC_B = "cam2"   # green, right in sbs


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
        print("ERROR: could not open the mix reader (port 11000).", file=sys.stderr)
        sys.exit(1)

    mode = "fs"
    rows = []
    print(f"Measuring {args.n} composite switches (fs<->sbs, hard cut)...")
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
    print(f"\nOK: {len(lat)}/{args.n}  median={st['median']} ms  p95={st['p95']} ms  "
          f"min={st['min']} max={st['max']}")
    print(f"  → {args.output_dir}/datos.csv , resumen.csv , datos.xlsx")


if __name__ == "__main__":
    main()
