#!/usr/bin/env python3
"""
Parses session .jsonl files and computes all metrics needed for TFG cap5:
  - Median CPU% and RAM% per camera count  (5.3.1 / 5.3.2)
  - Estimated energy in W using TDP        (5.3.2)
  - Internal bandwidth per N sources       (5.4 — theoretical)
  - Switching latency distribution         (5.3.3)

Usage — single session:
    python3 experiments/analyze_cameras.py <session.jsonl> <num_cameras>

Usage — multiple sessions at once:
    python3 experiments/analyze_cameras.py \\
        sessions/session31.jsonl 1 \\
        sessions/session32.jsonl 2 \\
        sessions/session33.jsonl 3 \\
        sessions/session34.jsonl 4
"""
import json
import sys
import statistics

WARMUP_ENTRIES  = 6      # skip first 30 s of warm-up (6 × 5 s STATE interval)
TDP_WATTS       = 45.0   # Intel i7-8750H TDP
BW_PER_CAM_MBPS = 622.08 # 1920×1080×1.5×25×8/1e6


# ── helpers ───────────────────────────────────────────────────────────────────

def parse_jsonl(path: str):
    entries = {"state": [], "latency": []}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = e.get("type")
            if t in entries:
                entries[t].append(e)
    return entries


def median_and_range(values):
    if not values:
        return None, None, None
    s = sorted(values)
    return round(statistics.median(s), 1), round(min(s), 1), round(max(s), 1)


def percentile(values, p):
    if not values:
        return None
    s = sorted(values)
    idx = max(0, int(len(s) * p / 100) - 1)
    return round(s[idx], 1)


# ── per-session analysis ───────────────────────────────────────────────────────

def analyse(jsonl_path: str, n_cams: int) -> dict:
    entries = parse_jsonl(jsonl_path)
    states   = entries["state"][WARMUP_ENTRIES:]
    latencies = entries["latency"]

    # ── CPU / RAM ──────────────────────────────────────────────────────────────
    cpu_vals = [e["system_health"]["cpu_usage_percent"] for e in states
                if "system_health" in e]
    ram_vals = [e["system_health"]["ram_usage_percent"] for e in states
                if "system_health" in e]

    cpu_med, cpu_min, cpu_max = median_and_range(cpu_vals)
    ram_med, ram_min, ram_max = median_and_range(ram_vals)

    energy_w = round(TDP_WATTS * cpu_med / 100.0, 1) if cpu_med else None

    # ── Bandwidth (theoretical) ────────────────────────────────────────────────
    bw_total_mbps = round(n_cams * BW_PER_CAM_MBPS, 1)
    bw_total_gbps = round(bw_total_mbps / 1000.0, 2)

    # ── Latency ───────────────────────────────────────────────────────────────
    lat_vals = [e["latency_ms"] for e in latencies if e.get("latency_ms") is not None]
    lat_med, lat_min, lat_max = median_and_range(lat_vals)
    lat_p95 = percentile(lat_vals, 95)

    # Histogram buckets for LaTeX (0-10, 10-20, ..., 50+ ms)
    buckets = {f"{lo}-{lo+10}": 0 for lo in range(0, 50, 10)}
    buckets["50+"] = 0
    for v in lat_vals:
        placed = False
        for lo in range(0, 50, 10):
            if v < lo + 10:
                buckets[f"{lo}-{lo+10}"] += 1
                placed = True
                break
        if not placed:
            buckets["50+"] += 1

    return {
        "n":            n_cams,
        "samples":      len(cpu_vals),
        "cpu_med":      cpu_med,
        "cpu_min":      cpu_min,
        "cpu_max":      cpu_max,
        "ram_med":      ram_med,
        "ram_min":      ram_min,
        "ram_max":      ram_max,
        "energy_w":     energy_w,
        "bw_mbps":      bw_total_mbps,
        "bw_gbps":      bw_total_gbps,
        "lat_n":        len(lat_vals),
        "lat_med":      lat_med,
        "lat_min":      lat_min,
        "lat_max":      lat_max,
        "lat_p95":      lat_p95,
        "lat_buckets":  buckets,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args or len(args) % 2 != 0:
        print(__doc__)
        sys.exit(1)

    pairs   = [(args[i], int(args[i + 1])) for i in range(0, len(args), 2)]
    results = sorted([analyse(p, n) for p, n in pairs], key=lambda r: r["n"])

    # ── CPU / RAM table ────────────────────────────────────────────────────────
    print("\n════ CPU / RAM per camera count ════")
    print(f"{'N':>3}  {'CPU med':>8}  {'CPU min':>7}  {'CPU max':>7}  "
          f"{'RAM med':>8}  {'RAM min':>7}  {'RAM max':>7}  {'Samples':>7}")
    print("─" * 68)
    for r in results:
        if r["cpu_med"] is None:
            print(f"{r['n']:>3}  {'NO DATA':>8}")
            continue
        print(f"{r['n']:>3}  {r['cpu_med']:>8}  {r['cpu_min']:>7}  {r['cpu_max']:>7}  "
              f"{r['ram_med']:>8}  {r['ram_min']:>7}  {r['ram_max']:>7}  {r['samples']:>7}")

    valid = [r for r in results if r["cpu_med"] is not None]
    if not valid:
        print("\nNo valid data.")
        return

    # ── LaTeX coordinates ──────────────────────────────────────────────────────
    print("\n════ LaTeX pgfplots coordinates ════")
    cpu_c  = " ".join(f"({r['n']},{r['cpu_med']})" for r in valid)
    ram_c  = " ".join(f"({r['n']},{r['ram_med']})" for r in valid)
    enrg_c = " ".join(f"({r['n']},{r['energy_w']})" for r in valid)
    print(f"CPU    : {cpu_c}")
    print(f"RAM    : {ram_c}")
    print(f"Energy : {enrg_c}")

    # ── Energy table ──────────────────────────────────────────────────────────
    print("\n════ Energy estimate (TDP={:.0f} W, i7-8750H) ════".format(TDP_WATTS))
    for r in valid:
        print(f"  N={r['n']}  CPU={r['cpu_med']}%  → {r['energy_w']} W")

    # ── Bandwidth table ────────────────────────────────────────────────────────
    print("\n════ Internal bandwidth (theoretical) ════")
    print(f"{'N':>3}  {'Per source':>12}  {'Total Mbps':>11}  {'Total Gbps':>11}")
    print("─" * 44)
    for r in results:
        print(f"{r['n']:>3}  {BW_PER_CAM_MBPS:>12.1f}  {r['bw_mbps']:>11.1f}  {r['bw_gbps']:>11.2f}")

    # ── Latency ───────────────────────────────────────────────────────────────
    lat_results = [r for r in results if r["lat_n"] > 0]
    if lat_results:
        print("\n════ Switching latency ════")
        for r in lat_results:
            print(f"  N={r['n']}  n={r['lat_n']}  "
                  f"median={r['lat_med']} ms  p95={r['lat_p95']} ms  "
                  f"min={r['lat_min']} ms  max={r['lat_max']} ms")

        # Histogram coordinates for pgfplots (ybar interval)
        r = lat_results[0]
        hist = r["lat_buckets"]
        buckets_order = [k for k in hist if k != "50+"] + ["50+"]
        print("\n  LaTeX histogram (ybar interval) — x=lower bucket edge, y=count:")
        coords = []
        edges = list(range(0, 60, 10))
        for i, lo in enumerate(range(0, 50, 10)):
            key = f"{lo}-{lo+10}"
            coords.append(f"({lo},{hist[key]})")
        coords.append(f"(50,{hist['50+']})")
        coords.append("(60,0)")
        print(f"  \\addplot coordinates {{{' '.join(coords)}}};")

if __name__ == "__main__":
    main()
