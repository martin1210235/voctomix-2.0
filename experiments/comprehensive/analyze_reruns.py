#!/usr/bin/env python3
"""Compara los escalados RE-EJECUTADOS (paper/pruebas/reruns/) con los oficiales y escribe
un informe (COMPARACION.md) con veredicto sobre la incongruencia de CPU entre escenarios.
No modifica nada oficial; solo genera el informe para decidir después."""
import csv
import os
import statistics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RERUNS = os.path.join(ROOT, "paper", "pruebas", "reruns")
FORMATS = ["1080p25", "1080p50", "2160p25", "2160p50"]
SCEN = ["docker", "local", "k8s"]


def medians(csvpath):
    if not os.path.isfile(csvpath):
        return None
    try:
        rows = list(csv.DictReader(open(csvpath, newline="")))
    except Exception:
        return None
    out = {}
    for k in range(0, 5):
        cpu = [float(r["cpu_pct"]) for r in rows if int(r.get("n_cameras_active", -1) or -1) == k and r.get("cpu_pct")]
        ram = [float(r["ram_pct"]) for r in rows if int(r.get("n_cameras_active", -1) or -1) == k and r.get("ram_pct")]
        if cpu:
            out[k] = (round(statistics.median(cpu), 1), round(statistics.median(ram), 1))
    return out


def main():
    lines = ["# Comparación de re-ejecuciones (escalados) vs oficiales\n"]
    lines.append("CPU% mediana por nº de cámaras (0→4). RERUN = nueva medida comparable.\n")
    for fmt in FORMATS:
        lines.append(f"\n## Formato {fmt}\n")
        lines.append("| escenario | fuente | 0c | 1c | 2c | 3c | 4c |")
        lines.append("|---|---|---|---|---|---|---|")
        for sc in SCEN:
            new = medians(os.path.join(RERUNS, f"{sc}_{fmt}", "1-1_escalado", "datos.csv"))
            old = medians(os.path.join(ROOT, "paper", "pruebas", f"{sc}_{fmt}", "1-1_escalado", "datos.csv"))
            for tag, m in (("RERUN", new), ("oficial", old)):
                if m is None:
                    lines.append(f"| {sc} | {tag} | — | — | — | — | — |")
                else:
                    cells = " | ".join(f"{m[k][0]:.0f}%" if k in m else "—" for k in range(5))
                    lines.append(f"| {sc} | {tag} | {cells} |")
        # veredicto anomalía CPU a 4 cams (rerun)
        r4 = {sc: (medians(os.path.join(RERUNS, f"{sc}_{fmt}", "1-1_escalado", "datos.csv")) or {}).get(4) for sc in SCEN}
        if all(r4.get(sc) for sc in SCEN):
            d, l, k = r4["docker"][0], r4["local"][0], r4["k8s"][0]
            verd = ("K8s ya NO sale más bajo → la incongruencia era estado de la máquina (RESUELTA)"
                    if k >= min(d, l) - 2 else
                    "K8s SIGUE más bajo que docker/local → puede ser real; revisar")
            lines.append(f"\n**4 cams (RERUN): docker={d:.0f}% local={l:.0f}% k8s={k:.0f}% → {verd}**")
    out = os.path.join(RERUNS, "COMPARACION.md")
    os.makedirs(RERUNS, exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"Informe escrito en {out}")


if __name__ == "__main__":
    main()
