#!/usr/bin/env bash
# Gestor del escenario KUBERNETES (k3s) para las pruebas del paper.
# Equivalente a local_scenario.sh pero desplegando en k3s.
#
# Reutiliza set_format.sh (config de voctocore) vía ConfigMap, despliega las
# fuentes de soporte y voctocore, y las cámaras por perfil (experiment/latency).
# Caída de cámara = kubectl delete pod (el Deployment la recrea = self-healing K8s).
#
# Uso:
#   k8s_scenario.sh up <fmt>                 -> namespace + configmap + soporte + voctocore
#   k8s_scenario.sh cams <fmt> <profile>     -> 4 cámaras (experiment|latency), espera ready
#   k8s_scenario.sh scale <N> <0|1>          -> activa/desactiva cámara N (escalado)
#   k8s_scenario.sh crash <N>                -> mata el pod de la cámara N (self-healing)
#   k8s_scenario.sh verify-format <fmt>      -> ffprobe del mix (:11000) confirma WxH@fps
#   k8s_scenario.sh mix-frame <archivo.png>  -> captura un frame del mix (:11000)
#   k8s_scenario.sh down                     -> borra el namespace (todo)
set -u
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$ROOT/k8s_escenario/experiments"
COMP="$ROOT/experiments/comprehensive"
NS="voctomix-exp"
TMP="/tmp/voctok8s"
mkdir -p "$TMP"

fmt_dims() {
  case "$1" in
    1080p25) W=1920; H=1080; F=25 ;;
    1080p50) W=1920; H=1080; F=50 ;;
    2160p25) W=3840; H=2160; F=25 ;;
    2160p50) W=3840; H=2160; F=50 ;;
    *) echo "formato inválido: $1" >&2; return 1 ;;
  esac
}

case "${1:-}" in
  up)
    fmt="${2:?fmt}"; fmt_dims "$fmt" || exit 1
    echo "[k8s] namespace"; kubectl apply -f "$HERE/namespace.yaml" >/dev/null
    echo "[k8s] set_format $fmt (config de voctocore)"; bash "$COMP/set_format.sh" "$fmt" >/dev/null
    echo "[k8s] configmap voctocore-config"
    kubectl create configmap voctocore-config -n "$NS" \
      --from-file=default-config.ini="$ROOT/voctocore/default-config.ini" \
      --dry-run=client -o yaml | kubectl apply -f - >/dev/null
    echo "[k8s] soporte (stream-blanker, audio, break, intro)"
    python3 "$HERE/gen_support_manifest.py" "$fmt" "$TMP/support.yaml" >/dev/null
    kubectl apply -f "$TMP/support.yaml" >/dev/null
    echo "[k8s] voctocore"; kubectl apply -f "$HERE/voctocore.yaml" >/dev/null
    # Si ya existían, reiniciar para recoger la nueva config (ConfigMap) sin duplicar RS.
    if kubectl get deploy voctocore -n "$NS" -o jsonpath='{.status.observedGeneration}' 2>/dev/null | grep -q '[2-9]'; then
      kubectl rollout restart deployment/voctocore deployment/support -n "$NS" >/dev/null 2>&1
    fi
    echo "[k8s] esperando voctocore ready..."
    kubectl rollout status deployment/voctocore -n "$NS" --timeout=180s
    ;;

  cams)
    fmt="${2:?fmt}"; profile="${3:?experiment|latency}"
    echo "[k8s] generando cámaras $fmt $profile"
    python3 "$HERE/gen_camera_manifests.py" "$fmt" "$profile" "$TMP/cams.yaml" >/dev/null
    kubectl apply -f "$TMP/cams.yaml" >/dev/null
    kubectl scale -n "$NS" deployment/cam1 deployment/cam2 deployment/cam3 deployment/cam4 --replicas=1 >/dev/null 2>&1
    echo "[k8s] esperando 4 cámaras ready..."
    for c in cam1 cam2 cam3 cam4; do kubectl rollout status deployment/$c -n "$NS" --timeout=120s; done
    ;;

  apply-cams)
    fmt="${2:?fmt}"; profile="${3:?experiment|latency}"
    echo "[k8s] aplicando cámaras $fmt $profile a replicas=0 (listas para escalado)"
    python3 "$HERE/gen_camera_manifests.py" "$fmt" "$profile" "$TMP/cams.yaml" >/dev/null
    kubectl apply -f "$TMP/cams.yaml" >/dev/null
    kubectl scale -n "$NS" deployment/cam1 deployment/cam2 deployment/cam3 deployment/cam4 --replicas=0 >/dev/null 2>&1
    echo "  cámaras aplicadas (0 activas)"
    ;;

  scale)
    N="${2:?N}"; R="${3:?0|1}"
    kubectl scale -n "$NS" deployment/cam$N --replicas="$R" >/dev/null && echo "  cam$N -> replicas=$R"
    ;;

  select)
    N="${2:?N}"
    python3 - "$N" <<'PY'
import socket, sys, time
n = sys.argv[1]
try:
    s = socket.create_connection(("127.0.0.1", 9999), timeout=5)
    time.sleep(0.5)
    s.sendall(f"set_video_a cam{n}\n".encode())
    time.sleep(1.5)
    s.close()
    print(f"  set_video_a cam{n} OK")
except Exception as e:
    print(f"  ERROR control 9999: {e}")
PY
    ;;

  crash)
    N="${2:?N}"
    kubectl delete pod -n "$NS" -l app=cam$N --grace-period=0 --force >/dev/null 2>&1 \
      && echo "  cam$N pod eliminado (Deployment lo recrea)"
    ;;

  verify-format)
    fmt="${2:?fmt}"; fmt_dims "$fmt" || exit 1
    echo "[k8s] ffprobe del mix (:11000)..."
    info=$(timeout 25 ffprobe -v error -select_streams v:0 \
      -show_entries stream=width,height,r_frame_rate,avg_frame_rate \
      -of default=noprint_wrappers=1 tcp://127.0.0.1:11000 2>/dev/null)
    echo "$info"
    echo "$info" | grep -q "width=$W" && echo "$info" | grep -q "height=$H" \
      && echo "  ANCHO/ALTO OK ($W x $H)" || echo "  ⚠ ANCHO/ALTO NO coincide (esperado $W x $H)"
    # Guardar evidencia por formato: ffprobe (texto) + un frame real (su resolución = la prueba).
    EVID="$ROOT/paper/pruebas/verificacion_formatos"; mkdir -p "$EVID"
    { echo "=== $(date '+%Y-%m-%d %H:%M:%S') | K8s | pedido: $fmt ($W x $H @ ${F}fps) ==="
      echo "$info"; echo; } >> "$EVID/ffprobe_k8s_${fmt}.txt"
    timeout 20 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 \
      -vf 'select=gte(t\,1)' -frames:v 1 "$EVID/frame_k8s_${fmt}.png" 2>/dev/null
    ;;

  mix-frame)
    out="${2:?archivo.png}"
    timeout 25 ffmpeg -y -nostdin -loglevel error -i tcp://127.0.0.1:11000 \
      -vf 'select=gte(t\,1)' -frames:v 1 "$out" 2>/dev/null
    [ -f "$out" ] && [ "$(stat -c%s "$out")" -gt 1000 ] && echo "  frame OK: $out" || echo "  ⚠ sin frame"
    ;;

  down)
    kubectl delete ns "$NS" --wait=true --timeout=120s 2>/dev/null
    echo "[k8s] namespace borrado"
    ;;

  *) echo "uso: k8s_scenario.sh up|cams|scale|crash|verify-format|mix-frame|down" >&2; exit 1 ;;
esac
