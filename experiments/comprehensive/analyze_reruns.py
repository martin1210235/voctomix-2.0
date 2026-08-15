#!/usr/bin/env python3
"""Compares the RE-RUN scaling tests (paper/pruebas/reruns/) against the official ones
and writes a report (COMPARACION.md) with a verdict on the CPU discrepancy between
scenarios. Does not modify anything official; only generates the report to decide later."""
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
    lines = ["# Re-run comparison (scaling tests) vs official\n"]
    lines.append("Median CPU% by number of cameras (0->4). RERUN = new, comparable measurement.\n")
    for fmt in FORMATS:
        lines.append(f"\n## Format {fmt}\n")
        lines.append("| scenario | source | 0c | 1c | 2c | 3c | 4c |")
        lines.append("|---|---|---|---|---|---|---|")
        for sc in SCEN:
            new = medians(os.path.join(RERUNS, f"{sc}_{fmt}", "1-1_escalado", "datos.csv"))
            old = medians(os.path.join(ROOT, "paper", "pruebas", f"{sc}_{fmt}", "1-1_escalado", "datos.csv"))
            for tag, m in (("RERUN", new), ("official", old)):
                if m is None:
                    lines.append(f"| {sc} | {tag} | — | — | — | — | — |")
                else:
                    cells = " | ".join(f"{m[k][0]:.0f}%" if k in m else "—" for k in range(5))
                    lines.append(f"| {sc} | {tag} | {cells} |")
        # verdict on the 4-cam CPU anomaly (rerun)
        r4 = {sc: (medians(os.path.join(RERUNS, f"{sc}_{fmt}", "1-1_escalado", "datos.csv")) or {}).get(4) for sc in SCEN}
        if all(r4.get(sc) for sc in SCEN):
            d, l, k = r4["docker"][0], r4["local"][0], r4["k8s"][0]
            verd = ("K8s is no longer lower -> the discrepancy was machine state (RESOLVED)"
                    if k >= min(d, l) - 2 else
                    "K8s is STILL lower than docker/local -> may be real; investigate")
            lines.append(f"\n**4 cams (RERUN): docker={d:.0f}% local={l:.0f}% k8s={k:.0f}% -> {verd}**")
    out = os.path.join(RERUNS, "COMPARACION.md")
    os.makedirs(RERUNS, exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"Informe escrito en {out}")


if __name__ == "__main__":
    main()
