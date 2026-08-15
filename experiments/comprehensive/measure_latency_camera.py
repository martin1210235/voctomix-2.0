#!/usr/bin/env python3
"""Analysis 2.1 — camera-switching video latency (direct cut).

For each switch: sends `set_video_a <cam>` over the control port and measures
the time until the mix output (port 11000) already shows the target camera's
colour marker. Metric in milliseconds.

  latency_ms = t(first mix frame with the target camera) - t(command sent)

Requires the stack running with all 4 cameras connected and the experiment
override (colour markers). Outputs: datos.csv, resumen.csv, datos.xlsx.

Usage:
  measure_latency_camera.py <output_dir> [--n 100] [--gap 2.5]
"""

import argparse
import os
import socket
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--gap", type=float, default=2.5, help="segundos entre conmutaciones")
    ap.add_argument("--ctrl-port", type=int, default=9999)
    ap.add_argument("--mix-port", type=int, default=11000)
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()

    s = socket.socket()
    s.settimeout(2.0)
    s.connect(("127.0.0.1", args.ctrl_port))
    time.sleep(0.4)
    send(s, "")
    send(s, "set_composite_mode fs")
    send(s, "set_video_a cam1")

    reader = MixCornerReader(args.mix_port)
    time.sleep(2.0)
    if not reader.alive():
        print("ERROR: could not open the mix reader (port 11000).", file=sys.stderr)
        sys.exit(1)

    current = "cam1"
    rows = []
    print(f"Measuring {args.n} camera switches (hard cut)...")
    for i in range(args.n):
        target = CYCLE[(CYCLE.index(current) + 1) % 4]  # always a different one
        # confirm the starting colour
        _, rgb0 = reader.current()
        t0 = time.monotonic()
        send(s, f"set_video_a {target}", wait=0.0)
        det = reader.wait_until(lambda c: c == target, after_t=t0, timeout=args.timeout)
        if det is None:
            rows.append({"iteration": i + 1, "from": current, "to": target,
                         "latency_ms": None, "status": "timeout"})
            print(f"  [{i+1:3d}] {current}->{target}  TIMEOUT")
        else:
            lat = round((det[0] - t0) * 1000, 1)
            rows.append({"iteration": i + 1, "from": current, "to": target,
                         "latency_ms": lat, "status": "ok"})
            print(f"  [{i+1:3d}] {current}->{target}  {lat} ms")
        current = target
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
