#!/usr/bin/env python3
"""Analysis 3.1 — resilience: camera failure and recovery time.

With the victim camera in fullscreen, simulates a realistic failure by killing
its ffmpeg process inside the container (`docker exec camN pkill -9 ffmpeg`).
Docker's restart policy restarts the container automatically; the time until
the victim's feed reappears in the mix output is measured.

Per iteration, records:
  detect_ms  = t(corner stops showing the victim)   - t(crash)   [detection]
  restore_ms = t(corner shows the victim again)      - t(detection) [recovery]
  mttr_ms    = t(feed restored)                       - t(crash)   [total recovery]

Built for the realistic config (BBB + markers). Rotates the victim cam1..cam4.
Outputs: datos.csv, resumen.csv, datos.xlsx.

Usage:
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
    ap.add_argument("--gap", type=float, default=8.0, help="stabilization time between iterations (s)")
    ap.add_argument("--ctrl-port", type=int, default=9999)
    ap.add_argument("--mix-port", type=int, default=11000)
    ap.add_argument("--loss-timeout", type=float, default=10.0)
    ap.add_argument("--recover-timeout", type=float, default=40.0)
    ap.add_argument("--scenario", default="docker", choices=["docker", "local", "k8s"],
                    help="docker: crash via docker exec; local: crash of the native ffmpeg; "
                         "k8s: kubectl delete pod (the Deployment recreates it)")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))

    def crash(victim):
        if args.scenario == "local":
            subprocess.run(["bash", os.path.join(here, "local_scenario.sh"), "crash", victim[-1]],
                           capture_output=True)
        elif args.scenario == "k8s":
            k8s = os.path.join(here, "..", "..", "k8s_escenario", "experiments", "k8s_scenario.sh")
            subprocess.run(["bash", k8s, "crash", victim[-1]], capture_output=True)
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
        print("ERROR: could not open the mix reader (port 11000).", file=sys.stderr)
        sys.exit(1)

    rows = []
    print(f"Measuring {args.n} camera failures and recoveries...")
    for i in range(args.n):
        victim = CYCLE[i % 4]
        other = CYCLE[(i + 1) % 4]
        # Put the victim in fullscreen and confirm it is visible.
        send(s, f"cut fs({victim},{other})")
        ready = reader.wait_until(lambda c: c == victim, time.monotonic(), timeout=8.0)
        if ready is None:
            rows.append({"iteration": i + 1, "victim": victim, "detect_ms": None,
                         "restore_ms": None, "mttr_ms": None, "status": "not_ready"})
            print(f"  [{i+1:3d}] {victim}  NOT READY (skipped)")
            time.sleep(2)
            continue
        time.sleep(1.0)

        t0 = time.monotonic()
        crash(victim)
        t_down = wait_color(reader, False, victim, t0, args.loss_timeout)
        if t_down is None:
            rows.append({"iteration": i + 1, "victim": victim, "detect_ms": None,
                         "restore_ms": None, "mttr_ms": None, "status": "no_loss"})
            print(f"  [{i+1:3d}] {victim}  no loss detected")
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
