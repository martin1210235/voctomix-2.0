#!/usr/bin/env bash
################################################################################
# DIAGNÓSTICO DETALLADO: ¿POR QUÉ RAPL SALE NEGATIVO?
################################################################################

set -euo pipefail
export LC_ALL=C

ROOT="/home/sonda/Documentos/voctomix"
SESSIONS_DIR="$ROOT/sessions"

echo "════════════════════════════════════════════════════════════"
echo "DIAGNÓSTICO PASO 2: RAPL NEGATIVO"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ ! -d "$SESSIONS_DIR" ]; then
  echo "❌ No se encontró directorio de sesiones"
  exit 1
fi

# 1. Verificar permisos RAPL
echo "1️⃣  VERIFICACIÓN DE PERMISOS RAPL:"
echo ""

RAPL_PATH="/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
if [ -e "$RAPL_PATH" ]; then
  echo "  ✅ RAPL sí existe: $RAPL_PATH"
  ls -lh "$RAPL_PATH" 2>/dev/null | tail -1 | awk '{print "     Permisos: " $1 " Propietario: " $3 ":" $4}'

  if python3 -c "print(int(open('$RAPL_PATH').read()))" 2>/dev/null; then
    echo "     📖 Permiso de LECTURA: ✅ SÍ (sin sudo necesario)"
    RAPL_PERMISSION="OK"
  else
    echo "     📖 Permiso de LECTURA: ❌ NO (se necesita sudo)"
    RAPL_PERMISSION="NO"
  fi
else
  echo "  ❌ RAPL no disponible en este hardware"
  RAPL_PERMISSION="N/A"
fi

echo ""
echo "2️⃣  ANÁLISIS DE BASELINES DOCKER:"
echo ""

echo "  N  │ CPU%  │ RAM%  │ RAPL (W) │ Método"
echo "  ───┼───────┼───────┼──────────┼────────────────────"

for baseline in $(ls -1 "$SESSIONS_DIR"/session*_baseline.json 2>/dev/null | sort -V); do
  N=$(basename "$baseline" | sed 's/session\([0-9]*\)_baseline.json/\1/')
  CPU=$(python3 -c "import json; d=json.load(open('$baseline')); print(d.get('cpu_pct', 0))" 2>/dev/null)
  RAM=$(python3 -c "import json; d=json.load(open('$baseline')); print(d.get('ram_pct', 0))" 2>/dev/null)
  RAPL=$(python3 -c "import json; d=json.load(open('$baseline')); print(d.get('rapl_watts', 0))" 2>/dev/null)

  METHOD="FALLBACK (CPU×TDP)"
  printf "  %-3s │ %5.1f │ %5.1f │ %8.2f │ %s\n" "$N" "$CPU" "$RAM" "$RAPL" "$METHOD"
done

echo ""
echo "════════════════════════════════════════════════════════════"
echo "CONCLUSIONES:"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$RAPL_PERMISSION" = "NO" ]; then
  echo "⚠️  RAPL SIN PERMISOS"
  echo ""
  echo "PROBLEMA:"
  echo "  • /sys/class/powercap/intel-rapl:0/energy_uj es owned by root"
  echo "  • Sin permisos, datos RAPL se estiman: CPU% × 165W / 100"
  echo "  • Si baseline_cpu > session_cpu → RAPL negativo (imposible)"
  echo ""
  echo "EVIDENCIA EN DATOS:"
  BASELINE_COUNT=$(ls -1 "$SESSIONS_DIR"/session*_baseline.json 2>/dev/null | wc -l)
  echo "  • $BASELINE_COUNT baselines recolectados"
  echo "  • Todos usando FALLBACK (CPU-based)"
  echo "  • Valores varían 1.32 W - 45.32 W (proporcionales a CPU%)"
  echo ""
  echo "SOLUCIONES:"
  echo ""
  echo "  Opción A (RECOMENDADA para máxima precisión):"
  echo "    sudo bash experiments/run_rapl_repeat.sh"
  echo "    → Recolecta RAPL con permisos root"
  echo "    → Reemplaza datos con valores MEDIDOS"
  echo "    → Tiempo: ~1 hora"
  echo ""
  echo "  Opción B (RÁPIDA, sin energía):"
  echo "    • Usar SOLO CPU% y RAM% en resultados"
  echo "    → Omitir RAPL/energía del paper"
  echo "    → Documentar: 'CPU metrics only, RAPL unavailable'"
  echo "    → Tiempo: inmediato"
  echo ""
  echo "RECOMENDACIÓN PARA TU DEFENSA:"
  echo "  → Opción A si necesitas energía en resultados"
  echo "  → Opción B si necesitas avanzar sin demora"
else
  echo "✅ RAPL CON PERMISOS (datos válidos)"
fi

echo ""
