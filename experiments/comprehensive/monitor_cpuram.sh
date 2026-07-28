#!/usr/bin/env bash
# Monitor EN VIVO para la demo: muestra CPU%, RAM% (misma fórmula que datos.csv, igual
# que htop) y la RESOLUCIÓN en uso (leída del config de voctocore). Resalta el cambio de
# resolución para que se vea claramente en el vídeo.
#   CPU% = 100*(1 - Δidle/Δtotal)   RAM% = 100*(MemTotal-MemAvailable)/MemTotal
# Uso:  monitor_cpuram.sh [segundos_entre_muestras]   (por defecto 2)
INT="${1:-2}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "  CPU/RAM (misma fórmula que datos.csv = htop) + RESOLUCIÓN en uso"
echo "  ------------------------------------------------------------------"
CFG="$ROOT/voctocore/default-config.ini" python3 - "$INT" <<'PY'
import sys, time, os, re
intv = float(sys.argv[1])
cfg = os.environ["CFG"]
def cpu():
    p = list(map(float, open("/proc/stat").readline().split()[1:8]))
    return p[3], sum(p)
def ram():
    m = {}
    for l in open("/proc/meminfo"):
        k, v = l.split(":"); m[k] = int(v.split()[0])
    return 100.0 * (m["MemTotal"] - m["MemAvailable"]) / m["MemTotal"]
def resolucion():
    try:
        for l in open(cfg):
            if l.strip().startswith("videocaps ="):
                w = re.search(r"width=(\d+)", l); h = re.search(r"height=(\d+)", l)
                f = re.search(r"framerate=(\d+)", l)
                if w and h and f:
                    return f"{w.group(1)}x{h.group(1)}@{f.group(1)}"
    except Exception:
        pass
    return "?"
i0, t0 = cpu(); prev_res = None
while True:
    time.sleep(intv)
    i1, t1 = cpu()
    c = 100.0 * (1 - (i1 - i0) / (t1 - t0)) if t1 > t0 else 0.0
    i0, t0 = i1, t1
    res = resolucion()
    if res != prev_res and prev_res is not None:
        print(f"  ===== RESOLUCIÓN CAMBIADA A {res} =====", flush=True)
    prev_res = res
    print(f"  {time.strftime('%H:%M:%S')}   CPU={c:5.1f}%   RAM={ram():4.1f}%   RESOLUCIÓN={res}", flush=True)
PY
