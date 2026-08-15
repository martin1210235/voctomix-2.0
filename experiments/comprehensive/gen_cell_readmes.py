#!/usr/bin/env python3
"""Generates a README.md per test cell (60) with: scenario, format, what is measured, how,
command, and the result (read from resumen.csv). Closes the per-test documentation gap."""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCEN = {"docker": "Docker", "local": "Local (native)", "k8s": "Kubernetes (k3s)"}
FMT = {"1080p25": (1920, 1080, 25), "1080p50": (1920, 1080, 50),
       "2160p25": (3840, 2160, 25), "2160p50": (3840, 2160, 50)}
ANALYSES = {
    "1-1_escalado": ("Performance — camera scaling",
                     "CPU (%) and RAM (%) usage read from /proc (the same source as htop) while "
                     "cameras 1->4 are activated in turn. Starts with 15 min at 0 cameras "
                     "(baseline), then 15 min per camera."),
    "1-2_sostenida": ("Performance — sustained load",
                      "CPU (%) and RAM (%) usage with 4 active cameras over 2 h."),
    "2-1_lat_camara": ("Latency — camera switching",
                       "Real (glass-to-glass) video latency when switching cameras via a hard cut, "
                       "detected by colour in the mix output. 100 repetitions."),
    "2-2_lat_composicion": ("Latency — composite switching",
                            "Real video latency when switching composite mode (fullscreen <-> "
                            "side-by-side) via a hard cut. 100 repetitions."),
    "3-1_resiliencia": ("Resilience — camera failure and recovery",
                        "A camera failure is forced and the MTTR (detection + "
                        "recovery) is measured on the mix output. 100 repetitions."),
}
CRASH = {"docker": "docker exec camN pkill -9 ffmpeg (container restart policy)",
         "local": "a native supervisor restarts the ffmpeg process (systemd-style)",
         "k8s": "kubectl delete pod (the Deployment recreates the pod = self-healing)"}


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
        L = ["| # cameras | Median CPU | Median RAM |", "|---|---|---|"]
        for k in range(5):
            L.append(f"| {k} | {med(f'{k}_cams','cpu_pct')}% | {med(f'{k}_cams','ram_pct')}% |")
        return "\n".join(L)
    if a == "1-2_sostenida":
        return f"Median CPU: **{med('ALL','cpu_pct')}%** · Median RAM: **{med('ALL','ram_pct')}%** (2 h, 4 cameras)."
    if a in ("2-1_lat_camara", "2-2_lat_composicion"):
        return f"Median latency: **{med('','latency_ms')} ms** (n=100)."
    if a == "3-1_resiliencia":
        return (f"Median MTTR: **{med('','mttr_ms')} ms** "
                f"(detection {med('','detect_ms')} ms + recovery {med('','restore_ms')} ms), n=100.")
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
                extra = f"\nFailure/recovery mechanism: {CRASH[sc]}.\n" if a == "3-1_resiliencia" else ""
                txt = f"""# {title}

**Scenario:** {SCEN[sc]} · **Format:** {fmt} ({w}x{h} @ {f} fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
{how}
{extra}
## Result
{result_block(sc, a, s)}

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
"""
                open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(txt)
                n += 1
    print(f"Generated {n} cell READMEs")


if __name__ == "__main__":
    main()
