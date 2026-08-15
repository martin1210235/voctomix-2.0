#!/bin/bash
# Render the full Docker figure set in a clean window: wait until no measurement
# process is running (matrix is between analyses/cells), then install seaborn and
# generate the figures. Runs on already-collected static Docker data.
set -u
cd /home/sonda/Documentos/voctomix
export MPLBACKEND=Agg
LOGDIR=paper/pruebas/graficas

# Wait for the current measurement to end (idle window = no measure_* running).
while pgrep -f "comprehensive/measure_" >/dev/null 2>&1; do
  sleep 15
done

echo "[render] clean window at $(date '+%H:%M:%S'); installing seaborn"
python3 -m pip install --user --quiet seaborn > "$LOGDIR/seaborn_install.log" 2>&1
echo "[render] seaborn rc=$?"

nice -n 19 python3 "$LOGDIR/generar_graficas_rendimiento.py" --scenario docker \
    > "$LOGDIR/render_rendimiento.log" 2>&1
echo "[render] rendimiento rc=$?"

nice -n 19 python3 "$LOGDIR/generar_graficas_latencia_resiliencia.py" --scenario docker \
    > "$LOGDIR/render_latres.log" 2>&1
echo "[render] latres rc=$? end at $(date '+%H:%M:%S')"

echo "=== figures generated ==="
ls -1 paper/figures/resultados/ 2>/dev/null
echo "=== log tails ==="
tail -6 "$LOGDIR/render_rendimiento.log"
tail -6 "$LOGDIR/render_latres.log"
