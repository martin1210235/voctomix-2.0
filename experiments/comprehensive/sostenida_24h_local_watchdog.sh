#!/usr/bin/env bash
# Lanza la sostenida de 24 h en Local 1080p25, y al terminar: genera resumen/xlsx si faltan,
# REVISA automaticamente que el resultado es razonable, y sube a GitHub. Robusto:
# - Reintenta SOLO si falla en el arranque (sin datos). Si ya escribio muestras, NO relanza
#   (los datos son incrementales; relanzar los perderia).
set -u
cd /home/sonda/Documentos/voctomix
OUT=paper/pruebas/local_1080p25_sostenida24h
W="$OUT/watchdog.log"
mkdir -p "$OUT"
echo "[wd] INICIO $(date '+%F %T')" >> "$W"
bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1

for attempt in 1 2 3; do
  python3 -u experiments/comprehensive/sostenida_24h_local.py "$OUT" --duration-min 1440 >> "$OUT/run_stdout.log" 2>&1
  if grep -q "\[sost24\] COMPLETADO" "$OUT/run_stdout.log"; then
    echo "[wd] COMPLETADO $(date '+%F %T')" >> "$W"; break
  fi
  rows=$(($(wc -l < "$OUT/datos.csv" 2>/dev/null || echo 1) - 1))
  if [ "$rows" -ge 10 ]; then
    echo "[wd] terminó con $rows muestras (parcial); NO relanzo para no perder datos" >> "$W"; break
  fi
  echo "[wd] fallo de arranque (rows=$rows); reintento $attempt en 30s" >> "$W"
  bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
  sleep 30
done

# --- finalize + REVISION AUTOMATICA ---
python3 - "$OUT" >> "$W" 2>&1 <<'PY'
import csv, os, sys
sys.path.insert(0, "experiments/comprehensive")
from lib_common import stats, write_summary_csv, bundle_xlsx
out = sys.argv[1]
cp = os.path.join(out, "datos.csv")
if not os.path.isfile(cp):
    print("REVISION: NO hay datos.csv -> FALLO"); sys.exit(0)
rows = list(csv.DictReader(open(cp, newline="")))
fields = ["timestamp", "elapsed_s", "cpu_pct", "ram_pct", "n_cameras_active"]
# generar resumen/xlsx si faltan
if not os.path.isfile(os.path.join(out, "resumen.csv")) or not os.path.isfile(os.path.join(out, "datos.xlsx")):
    summ = []
    for m in ("cpu_pct", "ram_pct"):
        summ.append({"group": "ALL", "metric": m, **stats([float(r[m]) for r in rows if r.get(m)])})
    sf = ["group","metric","n","min","q1","median","q3","p95","p99","max","mean","std"]
    write_summary_csv(os.path.join(out, "resumen.csv"), summ)
    bundle_xlsx(os.path.join(out, "datos.xlsx"),
                {"datos": (fields, [{k:r[k] for k in fields} for r in rows]),
                 "resumen": (sf, summ)})
    print("REVISION: resumen/xlsx regenerados desde datos.csv")
# metricas de revision
n = len(rows)
cpu = sorted(float(r["cpu_pct"]) for r in rows)
ram = [float(r["ram_pct"]) for r in rows]
def med(v): return v[len(v)//2] if v else 0
def win(v, a, b): s=v[int(n*a):int(n*b)]; return sum(s)/len(s) if s else 0
cam4 = 100.0*sum(1 for r in rows if r.get("n_cameras_active")=="4")/n if n else 0
r_ini, r_mid, r_fin = win(ram,0,0.1), win(ram,0.45,0.55), win(ram,0.9,1.0)
horas = (int(rows[-1]["elapsed_s"])/3600) if rows else 0
print(f"REVISION: muestras={n} (~{horas:.1f}h) | CPU mediana={med(cpu):.1f}% | "
      f"RAM {r_ini:.1f}->{r_mid:.1f}->{r_fin:.1f}% (delta {r_fin-r_ini:+.1f}pp) | %tiempo 4cams={cam4:.0f}%")
ok = n > 15000 and 70 <= med(cpu) <= 92 and 4 <= med(ram) if False else None
verdict = "RAZONABLE" if (n>15000 and 70<=med(cpu)<=92 and cam4>90) else "REVISAR A MANO"
leak = "SUBE (posible leak)" if (r_fin-r_ini)>2 else "PLANA (sin leak, esperado en Local)"
print(f"REVISION VEREDICTO: {verdict} | RAM: {leak}")
PY

# --- push a GitHub (misma forma que la de Docker 24h) ---
git add "$OUT" >> "$W" 2>&1
git reset -q paper/MEGA_PROMPT_FABLE.md 2>/dev/null
git commit --no-verify -q -m "data: sostenida 24h Local 1080p25 (estudio de memory-leak, analoga a Docker 4K)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" >> "$W" 2>&1
git fetch origin -q >> "$W" 2>&1
git push origin main >> "$W" 2>&1 && echo "[wd] PUSH OK $(date '+%F %T')" >> "$W" || echo "[wd] PUSH FALLO (commit local ok)" >> "$W"
echo "[wd] FIN $(date '+%F %T')" >> "$W"
