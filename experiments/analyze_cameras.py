#!/usr/bin/env python3
"""
Reads a session .jsonl file, filters STATE entries, and computes
median CPU% and RAM% — ready to paste into the LaTeX pgfplots coordinates.

Usage:
    python3 experiments/analyze_cameras.py <session.jsonl> <num_cameras>
    python3 experiments/analyze_cameras.py sessions/session1.jsonl 1

To summarise multiple sessions at once:
    python3 experiments/analyze_cameras.py sessions/session1.jsonl 1 \\
                                            sessions/session2.jsonl 2 \\
                                            sessions/session3.jsonl 3 \\
                                            sessions/session4.jsonl 4
"""
import json
import sys
import statistics


WARMUP_ENTRIES = 6  # skip first 30 s of warm-up (6 × 5 s STATE interval)


def analyse(jsonl_path: str, n_cams: int) -> dict:
    cpu_values = []
    ram_values = []

    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "state":
                continue
            health = entry.get("system_health", {})
            cpu = health.get("cpu_usage_percent")
            ram = health.get("ram_usage_percent")
            if cpu is not None:
                cpu_values.append(float(cpu))
            if ram is not None:
                ram_values.append(float(ram))

    if not cpu_values:
        return {"n": n_cams, "cpu": None, "ram": None, "samples": 0}

    cpu_trimmed = cpu_values[WARMUP_ENTRIES:]
    ram_trimmed = ram_values[WARMUP_ENTRIES:]

    return {
        "n": n_cams,
        "cpu": round(statistics.median(cpu_trimmed), 1) if cpu_trimmed else None,
        "ram": round(statistics.median(ram_trimmed), 1) if ram_trimmed else None,
        "samples": len(cpu_trimmed),
        "cpu_min": round(min(cpu_trimmed), 1),
        "cpu_max": round(max(cpu_trimmed), 1),
        "ram_min": round(min(ram_trimmed), 1),
        "ram_max": round(max(ram_trimmed), 1),
    }


def main():
    args = sys.argv[1:]
    if not args or len(args) % 2 != 0:
        print(__doc__)
        sys.exit(1)

    results = []
    pairs = [(args[i], int(args[i + 1])) for i in range(0, len(args), 2)]
    for path, n in pairs:
        r = analyse(path, n)
        results.append(r)

    results.sort(key=lambda x: x["n"])

    print("\n=== Per-session summary ===")
    print(f"{'N':>4}  {'CPU median':>10}  {'CPU min':>7}  {'CPU max':>7}  "
          f"{'RAM median':>10}  {'RAM min':>7}  {'RAM max':>7}  {'Samples':>7}")
    print("-" * 75)
    for r in results:
        if r["cpu"] is None:
            print(f"{r['n']:>4}  {'NO DATA':>10}")
            continue
        print(f"{r['n']:>4}  {r['cpu']:>10}  {r['cpu_min']:>7}  {r['cpu_max']:>7}  "
              f"{r['ram']:>10}  {r['ram_min']:>7}  {r['ram_max']:>7}  {r['samples']:>7}")

    valid = [r for r in results if r["cpu"] is not None]
    if not valid:
        print("\nNo valid data found.")
        return

    print("\n=== LaTeX pgfplots coordinates ===")
    cpu_coords = " ".join(f"({r['n']},{r['cpu']})" for r in valid)
    ram_coords = " ".join(f"({r['n']},{r['ram']})" for r in valid)
    print(f"CPU: {cpu_coords}")
    print(f"RAM: {ram_coords}")

    print("\n=== Energy estimate (TDP=45W, i7-8750H) ===")
    TDP = 45.0
    for r in valid:
        watts = round(TDP * r["cpu"] / 100.0, 1)
        print(f"  N={r['n']}  CPU={r['cpu']}%  → ~{watts} W")

    energy_coords = " ".join(
        f"({r['n']},{round(TDP * r['cpu'] / 100.0, 1)})" for r in valid
    )
    print(f"\nEnergy LaTeX coords: {energy_coords}")


if __name__ == "__main__":
    main()
