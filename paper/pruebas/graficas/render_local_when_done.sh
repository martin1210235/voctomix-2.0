#!/usr/bin/env bash
# Genera las gráficas de Local en cuanto la matriz Local termine (proceso ausente).
# Se ejecuta como 'bash <este script>' para que su línea de comando NO contenga el
# patrón buscado (evita el auto-match de pgrep).
set -u
cd /home/sonda/Documentos/voctomix
export MPLBACKEND=Agg
LOGDIR=paper/pruebas/graficas

while pgrep -f "run_matrix_local.py" >/dev/null 2>&1; do
  sleep 60
done

echo "[render-local] matriz Local terminada a $(date '+%H:%M:%S'); generando gráficas"
python3 "$LOGDIR/generar_graficas_rendimiento.py" --scenario local \
    > "$LOGDIR/render_local_rend.log" 2>&1
echo "[render-local] rendimiento rc=$?"
python3 "$LOGDIR/generar_graficas_latencia_resiliencia.py" --scenario local \
    > "$LOGDIR/render_local_latres.log" 2>&1
echo "[render-local] latres rc=$? fin a $(date '+%H:%M:%S')"
echo "=== gráficas local en paper/figures/resultados ==="
ls -1 paper/figures/resultados/ | grep local
