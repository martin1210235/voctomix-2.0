#!/usr/bin/env bash
# LIVE DEMO: changes the resolution AUTOMATICALLY every N seconds
# on the Local scenario, and demonstrates the change is real by showing:
#   - the config file (default-config.ini) with its videocaps changing,
#   - la salida real del mix verificada con ffprobe (ancho x alto @ fps),
#   - the output signal + the GUI on screen (show_gui.sh gui).
#
# Pausa la matriz K8s al empezar (usa los mismos puertos) y al terminar te recuerda
# how to resume it.
#
# Uso:  demo_resolucion.sh [segundos_por_formato]   (por defecto 120 = 2 min)
set -u
export DISPLAY="${DISPLAY:-:0}"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
ROOT="$(pwd)"
INTERVAL="${1:-120}"
CFG="voctocore/default-config.ini"
FORMATS=(1080p25 1080p50 2160p25 2160p50)

banner() { echo; echo "============================================================"; echo "   $1"; echo "============================================================"; }

banner "PAUSANDO la matriz de Kubernetes para la demo"
pkill -f run_matrix_k8s 2>/dev/null
pkill -f measure_performance_k8s 2>/dev/null
kubectl delete ns voctomix-exp --grace-period=0 --force 2>/dev/null
bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
echo "Waiting for port 9999 to be free..."
for i in $(seq 1 60); do ss -lnt 2>/dev/null | grep -q ":9999" || break; sleep 1; done
ss -lnt 2>/dev/null | grep -q ":9999" && echo "  AVISO: 9999 sigue ocupado" || echo "  9999 libre ✓"
echo "K8s pausado. Puertos libres para la demo Local."

for fmt in "${FORMATS[@]}"; do
    banner "CAMBIANDO RESOLUCION A:  $fmt"
    echo ">> videocaps BEFORE the change (file $CFG):"
    grep -E '^videocaps = ' "$CFG" | sed 's/,pixel.*//'
    echo
    echo ">> Ejecutando: set_format.sh $fmt"
    bash experiments/comprehensive/set_format.sh "$fmt" >/dev/null
    echo ">> videocaps AFTER the change (the file has changed):"
    grep -E '^videocaps = ' "$CFG" | sed 's/,pixel.*//'
    echo
    echo ">> Restarting voctocore + 4 cameras at the new format..."
    bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
    bash experiments/comprehensive/local_scenario.sh base_up >/dev/null 2>&1
    for n in 1 2 3 4; do bash experiments/comprehensive/local_scenario.sh cam_up "$n" experiment >/dev/null 2>&1; done
    sleep 30
    echo ">> Launching the output-signal viewer + the GUI..."
    bash experiments/comprehensive/show_gui.sh gui >/dev/null 2>&1
    sleep 3
    echo
    echo ">> VERIFICACION EN VIVO — ffprobe de la salida real del mix (:11000):"
    timeout 20 ffprobe -v error -select_streams v:0 \
        -show_entries stream=width,height,r_frame_rate,avg_frame_rate \
        -of default=noprint_wrappers=1 tcp://127.0.0.1:11000 2>/dev/null | sed 's/^/       /'
    echo
    echo "   >>> Format $fmt applied and verified. Watch htop: consumption changes with resolution."
    echo "   >>> Siguiente cambio en $((INTERVAL/60)) min $((INTERVAL%60)) s..."
    sleep "$INTERVAL"
done

banner "END OF DEMO — tearing down Local scenario"
bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
pkill -f "gst-launch.*port=11000" 2>/dev/null
pkill -f "python3 voctogui.py" 2>/dev/null
echo
echo "To RESUME the K8s test matrix (picks up from checkpoints where it left off):"
echo "  cd $ROOT && KUBECONFIG=$KUBECONFIG nohup python3 -u experiments/comprehensive/run_matrix_k8s.py >> paper/pruebas/matrix_k8s_run.log 2>&1 &"
