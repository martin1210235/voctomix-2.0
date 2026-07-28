#!/usr/bin/env python3
"""Rendimiento 1.1 (escalado de camaras) -> graficas seaborn para el paper.

Lee los datos.csv del analisis 1.1 de un escenario (por defecto Docker, 4 formatos),
agrega por numero de camaras activas y genera tres figuras en PDF (vectorial, LaTeX)
y PNG (preview):

  A  fig_<scn>_cpu_ram_2panel   -> 2 paneles CPU|RAM, 4 lineas de formato (RECOMENDADA)
  B  fig_<scn>_cpu_ram_8lineas  -> 1 grafica doble eje Y, 8 lineas (lo que pidieron)
  C  fig_<scn>_cpu_wideform     -> wide-form puro estilo ejemplo seaborn (solo CPU)

Uso:
  python3 generar_graficas_rendimiento.py                # Docker
  python3 generar_graficas_rendimiento.py --scenario local
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

SCENARIOS = {
    "docker": {
        "title": "Docker",
        "cells": {
            "1080p25": "paper/pruebas/docker_1080p25/1-1_escalado/datos.csv",
            "1080p50": "paper/pruebas/docker_1080p50/1-1_escalado/datos.csv",
            "2160p25": "paper/pruebas/docker_2160p25/1-1_escalado/datos.csv",
            "2160p50": "paper/pruebas/docker_2160p50/1-1_escalado/datos.csv",
        },
    },
    "local": {
        "title": "Local (nativo)",
        "cells": {
            "1080p25": "paper/pruebas/local_1080p25/1-1_escalado/datos.csv",
            "1080p50": "paper/pruebas/local_1080p50/1-1_escalado/datos.csv",
            "2160p25": "paper/pruebas/local_2160p25/1-1_escalado/datos.csv",
            "2160p50": "paper/pruebas/local_2160p50/1-1_escalado/datos.csv",
        },
    },
    "k8s": {
        "title": "Kubernetes (k3s)",
        "cells": {
            "1080p25": "paper/pruebas/k8s_1080p25/1-1_escalado/datos.csv",
            "1080p50": "paper/pruebas/k8s_1080p50/1-1_escalado/datos.csv",
            "2160p25": "paper/pruebas/k8s_2160p25/1-1_escalado/datos.csv",
            "2160p50": "paper/pruebas/k8s_2160p50/1-1_escalado/datos.csv",
        },
    },
}

FORMAT_LABELS = {
    "1080p25": "1080p @ 25 fps",
    "1080p50": "1080p @ 50 fps",
    "2160p25": "2160p @ 25 fps",
    "2160p50": "2160p @ 50 fps",
}
FORMAT_ORDER = ["1080p25", "1080p50", "2160p25", "2160p50"]


def load_cell(path):
    """Return per-camera-count medians (1..4) for a single cell, or None."""
    full = os.path.join(REPO, path)
    if not os.path.isfile(full):
        return None
    df = pd.read_csv(full)
    df = df[df["n_cameras_active"] >= 1]
    df = df[~((df["cpu_pct"] == 0.0) & (df["ram_pct"] == 0.0))]
    g = df.groupby("n_cameras_active").agg(
        cpu=("cpu_pct", "median"),
        ram=("ram_pct", "median"),
    )
    return g.reindex([1, 2, 3, 4])


def build_wide(scn):
    cpu, ram, present = {}, {}, []
    for fmt in FORMAT_ORDER:
        path = scn["cells"].get(fmt)
        g = load_cell(path) if path else None
        if g is None:
            print(f"  [aviso] sin datos para {fmt} ({path}) -> se omite")
            continue
        label = FORMAT_LABELS[fmt]
        cpu[label] = g["cpu"].values
        ram[label] = g["ram"].values
        present.append(label)
    idx = pd.Index([1, 2, 3, 4], name="Camaras activas")
    return (pd.DataFrame(cpu, index=idx),
            pd.DataFrame(ram, index=idx),
            present)


def fig_2panel(cpu_w, ram_w, title, out):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), sharex=True)
    sns.lineplot(data=cpu_w, palette="tab10", linewidth=2.4,
                 marker="o", markersize=8, ax=ax1, dashes=False)
    sns.lineplot(data=ram_w, palette="tab10", linewidth=2.4,
                 marker="o", markersize=8, ax=ax2, dashes=False)
    ax1.set_ylabel("Uso de CPU (%)")
    ax2.set_ylabel("Uso de RAM (%)")
    ax1.set_title("CPU")
    ax2.set_title("RAM")
    for ax in (ax1, ax2):
        ax.set_xlabel("Camaras activas")
        ax.set_xticks([1, 2, 3, 4])
        ax.margins(x=0.05)
    ax1.set_ylim(0, 100)
    ax1.legend(title="Formato", fontsize=8, title_fontsize=9)
    ax2.legend(title="Formato", fontsize=8, title_fontsize=9)
    fig.suptitle(f"Escenario {title}: escalado de recursos con el numero de camaras",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, out)


def fig_8lineas(cpu_w, ram_w, title, out):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax2 = ax.twinx()
    colors = sns.color_palette("tab10", len(cpu_w.columns))
    for c, col in zip(colors, cpu_w.columns):
        ax.plot(cpu_w.index, cpu_w[col], color=c, lw=2.4, marker="o",
                ms=7, ls="-", label=f"CPU {col}")
        ax2.plot(ram_w.index, ram_w[col], color=c, lw=2.0, marker="s",
                 ms=6, ls="--", label=f"RAM {col}")
    ax.set_xlabel("Camaras activas")
    ax.set_ylabel("Uso de CPU (%)  [linea solida]")
    ax2.set_ylabel("Uso de RAM (%)  [linea discontinua]")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_ylim(0, 100)
    ax2.set_ylim(0, 20)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.5, ncol=2, loc="upper left",
              framealpha=0.9)
    ax.set_title(f"Escenario {title}: CPU y RAM vs numero de camaras "
                 f"(4 formatos)", fontsize=12)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, out)


def fig_wideform(cpu_w, title, out):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    sns.lineplot(data=cpu_w, palette="tab10", linewidth=2.5,
                 marker="o", markersize=8, ax=ax, dashes=False)
    ax.set_xlabel("Camaras activas")
    ax.set_ylabel("Uso de CPU (%)")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_ylim(0, 100)
    ax.set_title(f"Escenario {title}: uso de CPU vs numero de camaras",
                 fontsize=12)
    ax.legend(title="Formato")
    fig.tight_layout()
    _save(fig, out)


def _save(fig, out):
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  guardada: {os.path.basename(out)}.pdf/.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="docker", choices=list(SCENARIOS))
    args = ap.parse_args()

    scn = SCENARIOS[args.scenario]
    sns.set_theme(style="whitegrid", context="notebook")
    outdir = os.path.join(REPO, "paper/figures/resultados")
    os.makedirs(outdir, exist_ok=True)

    print(f"Escenario: {scn['title']}")
    cpu_w, ram_w, present = build_wide(scn)
    if not present:
        print("ERROR: sin datos en ningun formato.")
        sys.exit(1)
    print(f"Formatos con datos: {', '.join(present)}")
    print("\nCPU (mediana %) por camaras:\n", cpu_w.round(1).to_string())
    print("\nRAM (mediana %) por camaras:\n", ram_w.round(1).to_string())

    tag = args.scenario
    print("\nGenerando figuras...")
    fig_2panel(cpu_w, ram_w, scn["title"], os.path.join(outdir, f"fig_{tag}_cpu_ram_2panel"))
    fig_8lineas(cpu_w, ram_w, scn["title"], os.path.join(outdir, f"fig_{tag}_cpu_ram_8lineas"))
    fig_wideform(cpu_w, scn["title"], os.path.join(outdir, f"fig_{tag}_cpu_wideform"))
    cpu_w.round(2).to_csv(os.path.join(outdir, f"tabla_{tag}_cpu_mediana.csv"))
    ram_w.round(2).to_csv(os.path.join(outdir, f"tabla_{tag}_ram_mediana.csv"))
    print("\nListo. Salida en paper/figures/resultados/")


if __name__ == "__main__":
    main()
