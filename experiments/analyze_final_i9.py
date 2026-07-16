#!/usr/bin/env python3
"""
Statistical analysis of final i9-10900X testing results (PASO 6).

Aggregates baseline CPU%, RAM% from all session baseline files and
latency/MTTR data from resilience JSON files, computes percentiles,
error bars, and generates formatted tables for paper + TFG.

Output:
  - Console summary table
  - JSON file with all statistics
"""

import json
import glob
import sys
import numpy as np
from pathlib import Path
from datetime import datetime


def load_baseline_metrics(sessions_dir):
    """Load all baseline CPU% and RAM% from session*_baseline*.json files."""
    cpu_values = []
    ram_values = []

    baseline_files = sorted(glob.glob(f"{sessions_dir}/session*_baseline*.json"))
    print(f"Found {len(baseline_files)} baseline files")

    for fpath in baseline_files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                if 'cpu_pct' in data:
                    cpu_values.append(data['cpu_pct'])
                if 'ram_pct' in data:
                    ram_values.append(data['ram_pct'])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read {fpath}: {e}", file=sys.stderr)

    return cpu_values, ram_values


def load_resilience_data(sessions_dir, prefix):
    """Load resilience JSON file and extract raw latency values."""
    fpath = f"{sessions_dir}/{prefix}.json"
    try:
        with open(fpath, 'r') as f:
            data = json.load(f)
            if 'raw_ms' in data:
                return data['raw_ms']
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read {fpath}: {e}", file=sys.stderr)
    return []


def compute_stats(values, name="metric"):
    """Compute comprehensive statistics for a dataset."""
    if not values:
        return None

    arr = np.array(values, dtype=float)
    arr = arr[~np.isnan(arr)]

    if len(arr) == 0:
        print(f"Warning: {name} has no valid values", file=sys.stderr)
        return None

    return {
        "count": int(len(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "median": float(np.median(arr)),
        "mean": float(np.mean(arr)),
        "std_dev": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "q25": float(np.percentile(arr, 25)),
        "q75": float(np.percentile(arr, 75)),
    }


def main():
    sessions_dir = Path(__file__).parent.parent / "sessions"

    print("\n" + "=" * 70)
    print("PASO 6: Statistical Analysis of i9-10900X Test Results")
    print("=" * 70)

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "hardware": "Intel Core i9-10900X",
        "categories": {}
    }

    cpu_vals, ram_vals = load_baseline_metrics(sessions_dir)
    print(f"\nBaseline metrics: {len(cpu_vals)} CPU samples, {len(ram_vals)} RAM samples")

    if cpu_vals:
        cpu_stats = compute_stats(cpu_vals, "CPU%")
        if cpu_stats:
            print(f"\nCPU% Statistics:")
            print(f"  Count  : {cpu_stats['count']}")
            print(f"  Min    : {cpu_stats['min']:.2f}%")
            print(f"  Q25    : {cpu_stats['q25']:.2f}%")
            print(f"  Median : {cpu_stats['median']:.2f}%")
            print(f"  Q75    : {cpu_stats['q75']:.2f}%")
            print(f"  Max    : {cpu_stats['max']:.2f}%")
            print(f"  Mean   : {cpu_stats['mean']:.2f}% ± {cpu_stats['std_dev']:.2f}%")
            print(f"  P95    : {cpu_stats['p95']:.2f}%")
            print(f"  P99    : {cpu_stats['p99']:.2f}%")
            all_results["categories"]["cpu_percent"] = cpu_stats

    if ram_vals:
        ram_stats = compute_stats(ram_vals, "RAM%")
        if ram_stats:
            print(f"\nRAM% Statistics:")
            print(f"  Count  : {ram_stats['count']}")
            print(f"  Min    : {ram_stats['min']:.2f}%")
            print(f"  Q25    : {ram_stats['q25']:.2f}%")
            print(f"  Median : {ram_stats['median']:.2f}%")
            print(f"  Q75    : {ram_stats['q75']:.2f}%")
            print(f"  Max    : {ram_stats['max']:.2f}%")
            print(f"  Mean   : {ram_stats['mean']:.2f}% ± {ram_stats['std_dev']:.2f}%")
            print(f"  P95    : {ram_stats['p95']:.2f}%")
            print(f"  P99    : {ram_stats['p99']:.2f}%")
            all_results["categories"]["ram_percent"] = ram_stats

    docker_latency = load_resilience_data(sessions_dir, "resilience_cam1")
    if docker_latency:
        docker_stats = compute_stats(docker_latency, "Docker MTTR")
        if docker_stats:
            print(f"\nDocker Resilience (MTTR in ms):")
            print(f"  Count  : {docker_stats['count']}")
            print(f"  Min    : {docker_stats['min']:.0f} ms")
            print(f"  Q25    : {docker_stats['q25']:.0f} ms")
            print(f"  Median : {docker_stats['median']:.0f} ms")
            print(f"  Q75    : {docker_stats['q75']:.0f} ms")
            print(f"  Max    : {docker_stats['max']:.0f} ms")
            print(f"  Mean   : {docker_stats['mean']:.0f} ms ± {docker_stats['std_dev']:.0f} ms")
            print(f"  P95    : {docker_stats['p95']:.0f} ms")
            print(f"  P99    : {docker_stats['p99']:.0f} ms")
            all_results["categories"]["docker_mttr_ms"] = docker_stats

    k8s_latency = load_resilience_data(sessions_dir, "resilience_cam1_k8s")
    if k8s_latency:
        k8s_stats = compute_stats(k8s_latency, "K8s MTTR")
        if k8s_stats:
            print(f"\nKubernetes Resilience (MTTR in ms):")
            print(f"  Count  : {k8s_stats['count']}")
            print(f"  Min    : {k8s_stats['min']:.0f} ms")
            print(f"  Q25    : {k8s_stats['q25']:.0f} ms")
            print(f"  Median : {k8s_stats['median']:.0f} ms")
            print(f"  Q75    : {k8s_stats['q75']:.0f} ms")
            print(f"  Max    : {k8s_stats['max']:.0f} ms")
            print(f"  Mean   : {k8s_stats['mean']:.0f} ms ± {k8s_stats['std_dev']:.0f} ms")
            print(f"  P95    : {k8s_stats['p95']:.0f} ms")
            print(f"  P99    : {k8s_stats['p99']:.0f} ms")
            all_results["categories"]["k8s_mttr_ms"] = k8s_stats

    output_file = sessions_dir / "analysis_final_i9.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n✓ Analysis saved to: {output_file}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
