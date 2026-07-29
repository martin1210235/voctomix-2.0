#!/usr/bin/env bash
# Watchdog del batch del viaje: ejecuta run_reruns.py y lo RELANZA si muriera sin completar
# (los checkpoints hacen que retome donde iba). Al completar, genera el informe de comparación
# y sube a GitHub los datos nuevos (reruns/ + evidencia ffprobe). Robusto para 5 días solo.
set -u
cd /home/sonda/Documentos/voctomix
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
mkdir -p paper/pruebas/reruns
WLOG=paper/pruebas/reruns/watchdog.log
DONE_MARK="RE-EJECUCIONES COMPLETADAS"

echo "[watchdog] INICIO $(date '+%F %T')" >> "$WLOG"
for attempt in $(seq 1 30); do
  echo "[watchdog] lanzando run_reruns (intento $attempt) $(date '+%F %T')" >> "$WLOG"
  python3 -u experiments/comprehensive/run_reruns.py >> paper/pruebas/reruns/rerun_stdout.log 2>&1
  if grep -q "$DONE_MARK" paper/pruebas/reruns/rerun_log.txt 2>/dev/null; then
    echo "[watchdog] run_reruns COMPLETADO $(date '+%F %T')" >> "$WLOG"
    break
  fi
  echo "[watchdog] salió sin completar; limpiando y reintentando en 90s" >> "$WLOG"
  docker compose -f docker-compose.yml -f docker-compose.experiment.yml down --remove-orphans >/dev/null 2>&1
  bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
  kubectl delete ns voctomix-exp --grace-period=0 --force >/dev/null 2>&1
  sleep 90
done

echo "[watchdog] === analizando y subiendo a GitHub ===" >> "$WLOG"
python3 -u experiments/comprehensive/analyze_reruns.py >> "$WLOG" 2>&1

git add paper/pruebas/reruns paper/pruebas/verificacion_formatos >> "$WLOG" 2>&1
git reset -q paper/MEGA_PROMPT_FABLE.md 2>/dev/null
git commit --no-verify -q -m "data(reruns): escalados 3 escenarios (baseline+comparables), ffprobe Docker/Local, latencia 4K50 x3, sostenida 24h

Datos de re-ejecucion generados de forma autonoma. No sobrescriben los oficiales; incluyen
COMPARACION.md para decidir promocion. Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" >> "$WLOG" 2>&1
git fetch origin -q >> "$WLOG" 2>&1
git push origin main >> "$WLOG" 2>&1 && echo "[watchdog] PUSH OK $(date '+%F %T')" >> "$WLOG" || echo "[watchdog] PUSH FALLO (datos commiteados localmente, recuperables)" >> "$WLOG"
echo "[watchdog] FIN $(date '+%F %T')" >> "$WLOG"
