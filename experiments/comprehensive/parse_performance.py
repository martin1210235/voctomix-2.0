#!/usr/bin/env python3
"""Analysis 1 (performance) — parse telemetry STATE events into CSV.

Reads a voctomix telemetry session (sessions/sessionN.jsonl), extracts CPU%,
RAM% and the number of active cameras per sample, and writes:
  - datos.csv     one row per telemetry sample (raw)
  - resumen.csv   descriptive stats, overall and grouped by active-camera count
  - datos.xlsx    convenience bundle (raw + summary sheets)

The active-camera count comes straight from the telemetry `sources` field, so
Analysis 1.1 (escalado 1->2->3->4) is labelled from real state, not assumed.

Usage:
  parse_performance.py <session.jsonl> <output_dir> [--label NAME]
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_common import stats, write_csv, write_summary_csv, bundle_xlsx  # noqa: E402

CAMS = ["cam1", "cam2", "cam3", "cam4"]


def parse_ts(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def load_samples(path):
    rows = []
    t0 = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            sh = d.get("system_health")
            if not sh or "cpu_usage_percent" not in sh:
                continue
            ts = parse_ts(d.get("timestamp", ""))
            if ts is None:
                continue
            if t0 is None:
                t0 = ts
            srcs = d.get("sources", {}) or {}
            active = {c: bool(srcs.get(c, False)) for c in CAMS}
            n_active = sum(active.values())
            comp = (d.get("composite") or {}).get("name", "unknown")
            rows.append({
                "timestamp": d.get("timestamp"),
                "elapsed_s": int((ts - t0).total_seconds()),
                "cpu_pct": sh.get("cpu_usage_percent"),
                "ram_pct": sh.get("ram_usage_percent"),
                "ram_available_mb": sh.get("ram_available_mb"),
                "n_cameras_active": n_active,
                "cam1": int(active["cam1"]),
                "cam2": int(active["cam2"]),
                "cam3": int(active["cam3"]),
                "cam4": int(active["cam4"]),
                "composite": comp,
            })
    return rows


def build_summary(rows):
    summary = []
    # overall
    for metric in ("cpu_pct", "ram_pct"):
        s = stats([r[metric] for r in rows])
        summary.append({"group": "ALL", "metric": metric, **s})
    # grouped by active-camera count
    for n in sorted({r["n_cameras_active"] for r in rows}):
        sub = [r for r in rows if r["n_cameras_active"] == n]
        for metric in ("cpu_pct", "ram_pct"):
            s = stats([r[metric] for r in sub])
            summary.append({"group": f"{n}_cams", "metric": metric, **s})
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("output_dir")
    ap.add_argument("--label", default="performance")
    args = ap.parse_args()

    rows = load_samples(args.session)
    if not rows:
        print(f"ERROR: no valid samples in {args.session}", file=sys.stderr)
        sys.exit(1)

    fields = ["timestamp", "elapsed_s", "cpu_pct", "ram_pct", "ram_available_mb",
              "n_cameras_active", "cam1", "cam2", "cam3", "cam4", "composite"]
    datos = os.path.join(args.output_dir, "datos.csv")
    resumen = os.path.join(args.output_dir, "resumen.csv")
    xlsx = os.path.join(args.output_dir, "datos.xlsx")

    write_csv(datos, fields, rows)
    summary = build_summary(rows)
    sfields = ["group", "metric", "n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std"]
    write_summary_csv(resumen, summary)
    bundle_xlsx(xlsx, {"datos": (fields, rows), "resumen": (sfields, summary)})

    dur = rows[-1]["elapsed_s"]
    print(f"[{args.label}] {len(rows)} samples, {dur}s duration")
    print(f"  → {datos}")
    print(f"  → {resumen}")
    print(f"  → {xlsx}")
    print("  CPU%/RAM% summary by number of cameras:")
    for s in summary:
        if s["group"] != "ALL":
            print(f"    {s['group']:>8}  {s['metric']:<8}  mediana={s['median']}  p95={s['p95']}  (n={s['n']})")


if __name__ == "__main__":
    main()
