#!/usr/bin/env bash
# DEMO EN VIVO: cambia la resolución AUTOMÁTICAMENTE cada N segundos
# en el escenario Local, y demuestra que el cambio es real mostrando:
#   - el fichero de config (default-config.ini) cambiando su videocaps,
#   - la salida real del mix verificada con ffprobe (ancho x alto @ fps),
#   - la señal de salida + la GUI en pantalla (show_gui.sh gui).
#
# Pausa la matriz K8s al empezar (usa los mismos puertos) y al terminar te recuerda
# cómo reanudarla.
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
echo "Esperando a que el puerto 9999 quede libre..."
for i in $(seq 1 60); do ss -lnt 2>/dev/null | grep -q ":9999" || break; sleep 1; done
ss -lnt 2>/dev/null | grep -q ":9999" && echo "  AVISO: 9999 sigue ocupado" || echo "  9999 libre ✓"
echo "K8s pausado. Puertos libres para la demo Local."

for fmt in "${FORMATS[@]}"; do
    banner "CAMBIANDO RESOLUCION A:  $fmt"
    echo ">> videocaps ANTES del cambio (fichero $CFG):"
    grep -E '^videocaps = ' "$CFG" | sed 's/,pixel.*//'
    echo
    echo ">> Ejecutando: set_format.sh $fmt"
    bash experiments/comprehensive/set_format.sh "$fmt" >/dev/null
    echo ">> videocaps DESPUES del cambio (el fichero ha cambiado):"
    grep -E '^videocaps = ' "$CFG" | sed 's/,pixel.*//'
    echo
    echo ">> Reiniciando voctocore + 4 cámaras al nuevo formato..."
    bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
    bash experiments/comprehensive/local_scenario.sh base_up >/dev/null 2>&1
    for n in 1 2 3 4; do bash experiments/comprehensive/local_scenario.sh cam_up "$n" experiment >/dev/null 2>&1; done
    sleep 30
    echo ">> Lanzando visor de la señal de salida + la GUI..."
    bash experiments/comprehensive/show_gui.sh gui >/dev/null 2>&1
    sleep 3
    echo
    echo ">> VERIFICACION EN VIVO — ffprobe de la salida real del mix (:11000):"
    timeout 20 ffprobe -v error -select_streams v:0 \
        -show_entries stream=width,height,r_frame_rate,avg_frame_rate \
        -of default=noprint_wrappers=1 tcp://127.0.0.1:11000 2>/dev/null | sed 's/^/       /'
    echo
    echo "   >>> Formato $fmt aplicado y verificado. Mira htop: el consumo cambia con la resolución."
    echo "   >>> Siguiente cambio en $((INTERVAL/60)) min $((INTERVAL%60)) s..."
    sleep "$INTERVAL"
done

banner "FIN DE LA DEMO — bajando escenario Local"
bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
pkill -f "gst-launch.*port=11000" 2>/dev/null
pkill -f "python3 voctogui.py" 2>/dev/null
echo
echo "Para REANUDAR la matriz K8s (retoma por checkpoints donde se quedó):"
echo "  cd $ROOT && KUBECONFIG=$KUBECONFIG nohup python3 -u experiments/comprehensive/run_matrix_k8s.py >> paper/pruebas/matrix_k8s_run.log 2>&1 &"
