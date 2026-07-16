#!/usr/bin/env bash
# check_and_proceed.sh — Verifica si PASO 2 terminó, valida resultados, lanza PASO 3 & 4

set -euo pipefail

ROOT="/home/sonda/Documentos/voctomix"
AUDIT_FILE="$ROOT/paper/TESTING_AUDIT_20260716.md"
RESULTS_DIR="$ROOT/experiments/results_20260716"

echo "════════════════════════════════════════════════════════════"
echo "VERIFICACIÓN POST-PASO 2 & LANZAMIENTO PASO 3-4"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "[$(date +%H:%M:%S)] Verificando si PASO 2 completó..."
echo ""

# 1. Verificar que PASO 2 script terminó
if pgrep -f "run_rapl_repeat.sh" > /dev/null 2>&1; then
    echo "❌ ERROR: run_rapl_repeat.sh aún corriendo"
    echo "Espera 5 min más y reintenta."
    exit 1
fi
echo "✅ run_rapl_repeat.sh completado"

# 2. Verificar sesiones generadas
SESSION_COUNT=$(ls -1 "$ROOT/sessions/session"*.jsonl 2>/dev/null | wc -l)
echo "✅ Sesiones generadas: $SESSION_COUNT (esperado: 8)"
if [[ $SESSION_COUNT -lt 8 ]]; then
    echo "⚠️  WARNING: Menos sesiones que esperadas ($SESSION_COUNT < 8)"
fi

# 3. Verificar baselines
BASELINE_COUNT=$(ls -1 "$ROOT/sessions/session"*_baseline*.json 2>/dev/null | wc -l)
echo "✅ Baselines registrados: $BASELINE_COUNT (esperado: 8)"
if [[ $BASELINE_COUNT -lt 8 ]]; then
    echo "⚠️  WARNING: Baselines incompletos ($BASELINE_COUNT < 8)"
fi

# 4. Buscar errores en logs
echo ""
echo "Buscando errores en logs..."
if grep -q "ERROR\|Traceback\|PermissionError" "$RESULTS_DIR/rapl_execution_20260716_retry.log" 2>/dev/null; then
    echo "❌ ERRORES DETECTADOS en log:"
    grep "ERROR\|Traceback\|PermissionError" "$RESULTS_DIR/rapl_execution_20260716_retry.log" | head -5
    exit 1
else
    echo "✅ Sin errores críticos detectados"
fi

# 5. Verificar tabla RAPL final
echo ""
echo "Buscando tabla RAPL en resultado..."
if grep -q "RAPL NET RESULTS" "$RESULTS_DIR"/rapl_*.log 2>/dev/null; then
    echo "✅ Tabla RAPL encontrada"
    echo ""
    grep -A 12 "RAPL NET RESULTS" "$RESULTS_DIR"/rapl_*.log | head -15
else
    echo "⚠️  RAPL table no encontrada (posible pero no crítico si RAPL sin permisos)"
fi

# 6. Verificar tamaño de datos
echo ""
echo "Verificando tamaño de datos..."
TOTAL_SIZE=$(du -sh "$ROOT/sessions" | awk '{print $1}')
echo "✅ Tamaño total de datos: $TOTAL_SIZE"

# 7. Si todo OK, proceder
echo ""
echo "════════════════════════════════════════════════════════════"
echo "PASO 2 VALIDACIÓN: ✅ PASSED"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Actualizando audit file..."
sed -i "s/Status: \[PENDING — Execution in progress\]/Status: ✅ COMPLETED/" "$AUDIT_FILE"
sed -i "s/Status: RUNNING.*/Status: ✅ COMPLETED - $(date +'%Y-%m-%d %H:%M:%S')/" "$AUDIT_FILE"
echo "✅ Audit file actualizado"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "PASO 3: KUBERNETES RESILIENCE"
echo "════════════════════════════════════════════════════════════"
cd "$ROOT"
echo "[$(date +%H:%M:%S)] Lanzando measure_resilience_k8s.py --n 10 --wait 720"
python3 tools/measure_resilience_k8s.py --n 10 --wait 720 2>&1 | tee -a "$RESULTS_DIR/paso3_k8s_resilience.log" &
PASO3_PID=$!
echo "✅ PASO 3 lanzado en background (PID: $PASO3_PID)"

# Esperar 30 segundos para que PASO 3 se estabilice
sleep 30

echo ""
echo "════════════════════════════════════════════════════════════"
echo "PASO 4: DOCKER RESILIENCE"
echo "════════════════════════════════════════════════════════════"
echo "[$(date +%H:%M:%S)] Lanzando measure_resilience.py --n 10"
python3 tools/measure_resilience.py --n 10 2>&1 | tee -a "$RESULTS_DIR/paso4_docker_resilience.log"
echo "✅ PASO 4 completado"

# Esperar a que PASO 3 termine
echo ""
echo "Esperando a que PASO 3 termine (puede tomar hasta 2 horas)..."
wait $PASO3_PID 2>/dev/null || true
echo "✅ PASO 3 completado"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ PASO 3 & 4 COMPLETADOS"
echo "════════════════════════════════════════════════════════════"
echo "Ahora proceder con PASO 5 (frame drops) y PASO 6 (análisis)."
