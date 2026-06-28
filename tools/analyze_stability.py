#!/usr/bin/env python3
"""
Reads a Voctomix telemetry JSONL session file and generates a stability graph
(CPU and RAM over time) suitable for inclusion in the TFG thesis.

Usage:
    python3 tools/analyze_stability.py <session.jsonl> [options]

Options:
    --output <path>       Output PNG path (default: memoria_tfg/figuras/estabilidad_30min.png)
    --max-minutes <N>     Truncate data after N minutes (default: no limit)
    --label <text>        Environment label for the plot title (default: "Docker Compose")
"""

import sys
import json
import os
import argparse
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__), "..", "memoria_tfg", "figuras", "estabilidad_30min.png"
)


def parse_jsonl(path, max_minutes=None):
    timestamps, cpu, ram = [], [], []
    t0 = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "state":
                continue
            ts_str = obj.get("timestamp", "")
            health = obj.get("system_health", {})
            cpu_val = health.get("cpu_usage_percent")
            ram_val = health.get("ram_usage_percent")
            if ts_str and cpu_val is not None and ram_val is not None:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if t0 is None:
                        t0 = ts
                    elapsed_min = (ts - t0).total_seconds() / 60.0
                    if max_minutes is not None and elapsed_min > max_minutes:
                        break
                    timestamps.append(ts)
                    cpu.append(float(cpu_val))
                    ram.append(float(ram_val))
                except ValueError:
                    continue
    return timestamps, cpu, ram


def to_minutes(timestamps):
    if not timestamps:
        return []
    t0 = timestamps[0]
    return [(t - t0).total_seconds() / 60.0 for t in timestamps]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session", help="Path to JSONL session file")
    parser.add_argument("--output", default=None,
                        help="Output PNG path")
    parser.add_argument("--max-minutes", type=float, default=None,
                        help="Truncate data after this many minutes")
    parser.add_argument("--label", default="Docker Compose",
                        help="Environment label for the plot title")
    args = parser.parse_args()

    out_path = os.path.abspath(args.output if args.output else DEFAULT_OUTPUT)

    if not os.path.exists(args.session):
        print(f"File not found: {args.session}")
        sys.exit(1)

    timestamps, cpu, ram = parse_jsonl(args.session, args.max_minutes)
    if not timestamps:
        print("No STATE events found in the file.")
        sys.exit(1)

    minutes = to_minutes(timestamps)
    duration = minutes[-1]
    n = len(timestamps)
    print(f"Environment  : {args.label}")
    print(f"Parsed       : {n} STATE events over {duration:.1f} minutes.")
    print(f"CPU  — mean: {np.mean(cpu):.1f}%  min: {np.min(cpu):.1f}%  max: {np.max(cpu):.1f}%")
    print(f"RAM  — mean: {np.mean(ram):.1f}%  min: {np.min(ram):.1f}%  max: {np.max(ram):.1f}%")

    fig, ax = plt.subplots(figsize=(13 / 2.54, 6 / 2.54))

    ax.plot(minutes, cpu, color="#CC5500", linewidth=1.2, label="CPU (%)")
    ax.plot(minutes, ram, color="#1a6faf", linewidth=1.2, label="RAM (%)")

    ax.set_xlabel("Tiempo transcurrido (min)", fontsize=9)
    ax.set_ylabel("Uso del sistema (%)", fontsize=9)
    ax.set_xlim(0, max(minutes) * 1.01)
    ax.set_ylim(0, 85)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    ax.legend(fontsize=8, loc="upper right")
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=0.4)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Figure saved : {out_path}")


if __name__ == "__main__":
    main()
