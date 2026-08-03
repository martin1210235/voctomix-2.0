#!/usr/bin/env python3
"""Genera un README.md por celda (60) con: escenario, formato, qué se mide, cómo, comando
y el resultado (leído del resumen.csv). Cierra el gap de documentación por prueba."""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCEN = {"docker": "Docker", "local": "Local (nativo)", "k8s": "Kubernetes (k3s)"}
FMT = {"1080p25": (1920, 1080, 25), "1080p50": (1920, 1080, 50),
       "2160p25": (3840, 2160, 25), "2160p50": (3840, 2160, 50)}
ANALYSES = {
    "1-1_escalado": ("Rendimiento — escalado de cámaras",
                     "Uso de CPU (%) y RAM (%) leídos de /proc (misma fuente que htop) mientras se "
                     "activan las cámaras 1→4. Empieza con 15 min a 0 cámaras (baseline) y luego 15 "
                     "min por cada cámara."),
    "1-2_sostenida": ("Rendimiento — carga sostenida",
                      "Uso de CPU (%) y RAM (%) con 4 cámaras activas durante 2 h."),
    "2-1_lat_camara": ("Latencia — conmutación de cámara",
                       "Latencia de vídeo real (glass-to-glass) al conmutar de cámara en corte, "
                       "detectada por color en la salida del mix. 100 repeticiones."),
    "2-2_lat_composicion": ("Latencia — conmutación de composición",
                            "Latencia de vídeo real al cambiar de composición (pantalla completa ↔ "
                            "side-by-side) en corte. 100 repeticiones."),
    "3-1_resiliencia": ("Resiliencia — caída y recuperación de cámara",
                        "Se fuerza la caída de una cámara y se mide el MTTR (detección + "
                        "restablecimiento) sobre la salida del mix. 100 repeticiones."),
}
CRASH = {"docker": "docker exec camN pkill -9 ffmpeg (restart policy del contenedor)",
         "local": "supervisor nativo reinicia el ffmpeg (systemd-style)",
         "k8s": "kubectl delete pod (el Deployment recrea el pod = self-healing)"}


def summ(path):
    if not os.path.isfile(path):
        return {}
    out = {}
    for r in csv.DictReader(open(path, newline="")):
        out[(r.get("group", ""), r.get("metric", ""))] = r
    return out


def result_block(sc, a, s):
    def med(g, m):
        r = s.get((g, m))
        return f"{float(r['median']):.1f}" if r and r.get("median") else "—"
    if a == "1-1_escalado":
        L = ["| nº cámaras | CPU mediana | RAM mediana |", "|---|---|---|"]
        for k in range(5):
            L.append(f"| {k} | {med(f'{k}_cams','cpu_pct')}% | {med(f'{k}_cams','ram_pct')}% |")
        return "\n".join(L)
    if a == "1-2_sostenida":
        return f"CPU mediana: **{med('ALL','cpu_pct')}%** · RAM mediana: **{med('ALL','ram_pct')}%** (2 h, 4 cámaras)."
    if a in ("2-1_lat_camara", "2-2_lat_composicion"):
        return f"Latencia mediana: **{med('','latency_ms')} ms** (n=100)."
    if a == "3-1_resiliencia":
        return (f"MTTR mediana: **{med('','mttr_ms')} ms** "
                f"(detección {med('','detect_ms')} ms + restablecimiento {med('','restore_ms')} ms), n=100.")
    return ""


def main():
    n = 0
    for sc in SCEN:
        for fmt, (w, h, f) in FMT.items():
            for a, (title, how) in ANALYSES.items():
                d = os.path.join(ROOT, "paper", "pruebas", f"{sc}_{fmt}", a)
                if not os.path.isdir(d):
                    continue
                s = summ(os.path.join(d, "resumen.csv"))
                extra = f"\nMecanismo de caída/recuperación: {CRASH[sc]}.\n" if a == "3-1_resiliencia" else ""
                txt = f"""# {title}

**Escenario:** {SCEN[sc]} · **Formato:** {fmt} ({w}×{h} @ {f} fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (aplicaciones cerradas).

## Qué se mide
{how}
{extra}
## Resultado
{result_block(sc, a, s)}

## Ficheros
`datos.csv` (datos crudos), `resumen.csv` (estadística), `datos.xlsx` (Excel). El formato de
la salida se verificó con ffprobe (ver `paper/pruebas/verificacion_formatos/`).
"""
                open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(txt)
                n += 1
    print(f"Generados {n} README de celda")


if __name__ == "__main__":
    main()
