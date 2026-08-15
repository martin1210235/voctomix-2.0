#!/usr/bin/env python3
"""Latency (2.1, 2.2) and resilience (3.1) -> seaborn figures for the paper.

Reads the raw datos.csv for a scenario (Docker by default, 4 formats) and generates:

  fig_<scn>_latencia_formato      -> latency boxplot (camera vs composite) by format
  fig_<scn>_resiliencia_mttr      -> stacked bar detect+restore (=MTTR) by format
  fig_<scn>_resiliencia_box       -> MTTR boxplot by format

Output in paper/figures/resultados/ (vector PDF + PNG).
Paper's message: latency and MTTR are practically independent of resolution.

Usage:
  python3 generar_graficas_latencia_resiliencia.py                 # Docker
  python3 generar_graficas_latencia_resiliencia.py --scenario local
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

REPO = "/home/sonda/Documentos/voctomix"
OUTDIR = os.path.join(REPO, "paper/figures/resultados")

FORMAT_LABELS = {
    "1080p25": "1080p25", "1080p50": "1080p50",
    "2160p25": "2160p25", "2160p50": "2160p50",
}
FORMAT_ORDER = ["1080p25", "1080p50", "2160p25", "2160p50"]

SCENARIOS = {
    "docker": {
        "title": "Docker",
        "base": {
            "1080p25": "paper/pruebas/docker_1080p25",
            "1080p50": "paper/pruebas/docker_1080p50",
            "2160p25": "paper/pruebas/docker_2160p25",
            "2160p50": "paper/pruebas/docker_2160p50",
        },
    },
    "local": {
        "title": "Local (native)",
        "base": {
            "1080p25": "paper/pruebas/local_1080p25",
            "1080p50": "paper/pruebas/local_1080p50",
            "2160p25": "paper/pruebas/local_2160p25",
            "2160p50": "paper/pruebas/local_2160p50",
        },
    },
    "k8s": {
        "title": "Kubernetes (k3s)",
        "base": {
            "1080p25": "paper/pruebas/k8s_1080p25",
            "1080p50": "paper/pruebas/k8s_1080p50",
            "2160p25": "paper/pruebas/k8s_2160p25",
            "2160p50": "paper/pruebas/k8s_2160p50",
        },
    },
}


def read_csv(base, sub):
    full = os.path.join(REPO, base, sub, "datos.csv")
    return pd.read_csv(full) if os.path.isfile(full) else None


def load_latency(scn):
    rows = []
    for fmt in FORMAT_ORDER:
        base = scn["base"].get(fmt)
        if not base:
            continue
        for sub, tipo in (("2-1_lat_camara", "Camera switching"),
                          ("2-2_lat_composicion", "Composite switching")):
            df = read_csv(base, sub)
            if df is None:
                continue
            df = df[df["status"] == "ok"]
            for v in df["latency_ms"].values:
                rows.append({"Format": FORMAT_LABELS[fmt], "Latency (ms)": v,
                             "Type": tipo})
    return pd.DataFrame(rows)


def load_resilience(scn):
    rows = []
    for fmt in FORMAT_ORDER:
        base = scn["base"].get(fmt)
        if not base:
            continue
        df = read_csv(base, "3-1_resiliencia")
        if df is None:
            continue
        df = df[df["status"] == "ok"]
        rows.append({
            "Format": FORMAT_LABELS[fmt],
            "detect": df["detect_ms"].median(),
            "restore": df["restore_ms"].median(),
            "mttr_med": df["mttr_ms"].median(),
            "mttr_all": df["mttr_ms"].values,
        })
    return rows


def fig_latencia(scn, out):
    data = load_latency(scn)
    if data.empty:
        print("  [warning] no latency data")
        return
    fig, ax = plt.subplots(figsize=(8.5, 5))
    sns.boxplot(data=data, x="Format", y="Latency (ms)", hue="Type",
                order=[FORMAT_LABELS[f] for f in FORMAT_ORDER],
                palette="tab10", width=0.6, fliersize=2, ax=ax)
    ax.set_title(f"Scenario {scn['title']}: switching latency by format "
                 f"(n=100 per box)", fontsize=12)
    ax.set_xlabel("Video format")
    ax.legend(title="", fontsize=9)
    ax.margins(y=0.08)
    fig.tight_layout()
    _save(fig, out)


def fig_resiliencia_stacked(scn, out):
    rows = load_resilience(scn)
    if not rows:
        print("  [warning] no resilience data")
        return
    labels = [r["Format"] for r in rows]
    detect = np.array([r["detect"] for r in rows])
    restore = np.array([r["restore"] for r in rows])
    pal = sns.color_palette("tab10")
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    ax.bar(x, detect, width=0.55, label="Detection", color=pal[0])
    ax.bar(x, restore, width=0.55, bottom=detect, label="Recovery",
           color=pal[1])
    for i, r in enumerate(rows):
        ax.text(i, detect[i] + restore[i] + 25, f"{r['mttr_med']:.0f} ms",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Time (ms)")
    ax.set_xlabel("Video format")
    ax.set_title(f"Scenario {scn['title']}: camera recovery MTTR "
                 f"(detection + recovery)", fontsize=12)
    ax.legend(title="", fontsize=9)
    ax.margins(y=0.12)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save(fig, out)


def fig_resiliencia_box(scn, out):
    rows = load_resilience(scn)
    if not rows:
        return
    data = []
    for r in rows:
        for v in r["mttr_all"]:
            data.append({"Format": r["Format"], "MTTR (ms)": v})
    data = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=data, x="Format", y="MTTR (ms)",
                order=[r["Format"] for r in rows], palette="tab10",
                width=0.5, fliersize=2, ax=ax)
    ax.set_title(f"Scenario {scn['title']}: MTTR distribution by format "
                 f"(n=100)", fontsize=12)
    ax.set_xlabel("Video format")
    fig.tight_layout()
    _save(fig, out)


def _save(fig, out):
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {os.path.basename(out)}.pdf/.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="docker", choices=list(SCENARIOS))
    args = ap.parse_args()
    scn = SCENARIOS[args.scenario]
    sns.set_theme(style="whitegrid", context="notebook")
    os.makedirs(OUTDIR, exist_ok=True)
    tag = args.scenario
    print(f"Scenario: {scn['title']} -> latency and resilience")
    fig_latencia(scn, os.path.join(OUTDIR, f"fig_{tag}_latencia_formato"))
    fig_resiliencia_stacked(scn, os.path.join(OUTDIR, f"fig_{tag}_resiliencia_mttr"))
    fig_resiliencia_box(scn, os.path.join(OUTDIR, f"fig_{tag}_resiliencia_box"))
    print("\nDone. Output in paper/figures/resultados/")


if __name__ == "__main__":
    main()
