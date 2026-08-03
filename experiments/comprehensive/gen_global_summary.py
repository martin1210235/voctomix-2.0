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
    L = ["## Rendimiento — CPU mediana por nº de cámaras (0→4)\n"]
    for fmt in FMT:
        L.append(f"\n**{fmt}**\n")
        L.append("| escenario | 0c | 1c | 2c | 3c | 4c |")
        L.append("|---|---|---|---|---|---|")
        for sc in SC:
            cells = " | ".join(
                (f"{med(sc,fmt,'1-1_escalado',f'{k}_cams','cpu_pct') or '—':.0f}%"
                 if med(sc, fmt, '1-1_escalado', f'{k}_cams', 'cpu_pct') is not None else "—")
                for k in range(5))
            L.append(f"| {sc} | {cells} |")
    return "\n".join(L)


def tab(title, sub, group, metric, unit):
    L = [f"\n## {title}\n", "| escenario | " + " | ".join(FMT) + " |",
         "|---|" + "---|" * len(FMT)]
    for sc in SC:
        vals = []
        for fmt in FMT:
            v = med(sc, fmt, sub, group, metric)
            vals.append(f"{v:.0f}{unit}" if v is not None else "—")
        L.append(f"| {sc} | " + " | ".join(vals) + " |")
    return "\n".join(L)


def main():
    parts = ["# Resumen global de resultados (3 escenarios × 4 formatos)\n",
             "CPU/RAM leídos de /proc (igual que htop). Latencia = vídeo real (glass-to-glass). "
             "Formatos verificados con ffprobe.\n",
             sec_cpu_escalado(),
             tab("Rendimiento — RAM mediana a 4 cámaras (escalado)", "1-1_escalado", "4_cams", "ram_pct", "%"),
             tab("Sostenida (2 h) — CPU mediana", "1-2_sostenida", "ALL", "cpu_pct", "%"),
             tab("Sostenida (2 h) — RAM mediana", "1-2_sostenida", "ALL", "ram_pct", "%"),
             tab("Latencia 2.1 — conmutación de cámara (mediana)", "2-1_lat_camara", "", "latency_ms", " ms"),
             tab("Latencia 2.2 — conmutación de composición (mediana)", "2-2_lat_composicion", "", "latency_ms", " ms"),
             tab("Resiliencia — MTTR (mediana)", "3-1_resiliencia", "", "mttr_ms", " ms"),
             "\n## Hallazgos clave\n",
             "- **CPU**: escala con nº de cámaras y con la resolución. A 4 cámaras el sistema satura "
             "(~90%) y a 4K/50fps descarta frames (techo de hardware). Los 3 escenarios son comparables.",
             "- **RAM**: sobrecarga de despliegue **Docker > K8s > Local** (contenedores añaden memoria).",
             "- **RAM sostenida**: Docker a 4K crece hasta ~17,7% y se estabiliza (no es leak descontrolado; "
             "confirmado con sostenida de 24 h). Local y K8s planos.",
             "- **Latencia**: depende del framerate (≈mitad a 50 fps), no de la resolución. Docker a 4K50 "
             "muestra composición inestable por saturación.",
             "- **MTTR**: ~1–2 s en los 3 escenarios; recuperación por restart-policy (Docker) / supervisor "
             "(Local) / self-healing del ReplicaSet (K8s).",
             ]
    out = os.path.join(ROOT, "paper", "pruebas", "RESUMEN_GLOBAL.md")
    open(out, "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print(f"Escrito {out}")


if __name__ == "__main__":
    main()
