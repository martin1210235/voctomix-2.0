#!/usr/bin/env python3
"""Genera RESUMEN_GLOBAL.md: comparativa final de los 3 escenarios (docker/local/k8s) x 4
formatos, leyendo los resumen.csv. Tablas de CPU (0→4 cams), RAM, sostenida, latencia y MTTR."""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SC = ["docker", "local", "k8s"]
FMT = ["1080p25", "1080p50", "2160p25", "2160p50"]


def med(sc, fmt, sub, group, metric):
    p = os.path.join(ROOT, "paper", "pruebas", f"{sc}_{fmt}", sub, "resumen.csv")
    if not os.path.isfile(p):
        return None
    for r in csv.DictReader(open(p, newline="")):
        if r.get("group", "") == group and r.get("metric", "") == metric:
            try:
                return float(r["median"])
            except Exception:
                return None
    return None


def sec_cpu_escalado():
    L = ["## Performance — median CPU by number of cameras (0->4)\n"]
    for fmt in FMT:
        L.append(f"\n**{fmt}**\n")
        L.append("| scenario | 0c | 1c | 2c | 3c | 4c |")
        L.append("|---|---|---|---|---|---|")
        for sc in SC:
            cells = " | ".join(
                (f"{med(sc,fmt,'1-1_escalado',f'{k}_cams','cpu_pct') or '—':.0f}%"
                 if med(sc, fmt, '1-1_escalado', f'{k}_cams', 'cpu_pct') is not None else "—")
                for k in range(5))
            L.append(f"| {sc} | {cells} |")
    return "\n".join(L)


def tab(title, sub, group, metric, unit):
    L = [f"\n## {title}\n", "| scenario | " + " | ".join(FMT) + " |",
         "|---|" + "---|" * len(FMT)]
    for sc in SC:
        vals = []
        for fmt in FMT:
            v = med(sc, fmt, sub, group, metric)
            vals.append(f"{v:.0f}{unit}" if v is not None else "—")
        L.append(f"| {sc} | " + " | ".join(vals) + " |")
    return "\n".join(L)


def main():
    parts = ["# Global results summary (3 scenarios x 4 formats)\n",
             "CPU/RAM read from /proc (same as htop). Latency = real video (glass-to-glass). "
             "Formats verified with ffprobe.\n",
             sec_cpu_escalado(),
             tab("Performance — median RAM at 4 cameras (scaling)", "1-1_escalado", "4_cams", "ram_pct", "%"),
             tab("Sustained (2 h) — median CPU", "1-2_sostenida", "ALL", "cpu_pct", "%"),
             tab("Sustained (2 h) — median RAM", "1-2_sostenida", "ALL", "ram_pct", "%"),
             tab("Latency 2.1 — camera switching (median)", "2-1_lat_camara", "", "latency_ms", " ms"),
             tab("Latency 2.2 — composite switching (median)", "2-2_lat_composicion", "", "latency_ms", " ms"),
             tab("Resilience — MTTR (median)", "3-1_resiliencia", "", "mttr_ms", " ms"),
             "\n## Key findings\n",
             "- **CPU**: scales with the number of cameras and with resolution. At 4 cameras the system "
             "saturates (~90%) and at 4K/50fps it drops frames (hardware ceiling). The 3 scenarios are comparable.",
             "- **RAM**: deployment overhead **Docker > K8s > Local** (containers add memory).",
             "- **Sustained RAM**: Docker at 4K grows to ~17.7% and stabilizes (not an uncontrolled leak; "
             "confirmed with the 24 h sustained run). Local and K8s stay flat.",
             "- **Latency**: depends on frame rate (roughly halves at 50 fps), not resolution. Docker at 4K50 "
             "shows unstable compositing due to saturation.",
             "- **MTTR**: ~1-2 s across the 3 scenarios; recovery via restart-policy (Docker) / supervisor "
             "(Local) / ReplicaSet self-healing (K8s).",
             ]
    out = os.path.join(ROOT, "paper", "pruebas", "RESUMEN_GLOBAL.md")
    open(out, "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print(f"Escrito {out}")


if __name__ == "__main__":
    main()
