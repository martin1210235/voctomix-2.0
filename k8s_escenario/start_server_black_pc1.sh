#!/bin/bash
set -euo pipefail

# Starts the Kubernetes server with all cameras outputting black.
# Cameras stay silent and ready — inject sources later with inject_cam.sh.

export MINIKUBE_IN_STYLE=false
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

PF_PID=""

log() { echo "[$(date +%H:%M:%S)] $*"; }

cleanup() {
    log "Server shutdown detected. Stopping port-forward..."
    [[ -n "$PF_PID" ]] && kill $PF_PID 2>/dev/null || true
    log "System stopped. Run 'minikube stop' to shut down the cluster."
}
trap cleanup EXIT INT TERM

inject_black() {
    local container="$1"
    local port="$2"
    log "Setting $container to black..."
    kubectl exec deployment/studio -c "$container" -- \
        bash -c "pkill ffmpeg 2>/dev/null || true; sleep 0.5; \
        ffmpeg -loglevel error -re \
            -f lavfi -i color=black:s=\${WIDTH}x\${HEIGHT}:r=\${FRAMERATE} \
            -f lavfi -i anullsrc=r=\${AUDIORATE}:cl=stereo \
            -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
            -f matroska tcp://localhost:$port > /dev/null 2>&1 &" 2>/dev/null || \
        log "Warning: could not set $container to black (container may not be ready)"
}

is_minikube_ready() {
    minikube status 2>/dev/null | grep -q "apiserver: Running"
}

is_studio_ready() {
    local pod
    pod=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
    [[ -z "$pod" ]] && return 1
    local not_ready
    not_ready=$(kubectl get pod "$pod" \
        -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null \
        | tr ' ' '\n' | grep -c "false" || true)
    [[ "$not_ready" -eq 0 ]]
}

wait_for_ready() {
    local pod="$1"
    local attempts="${2:-40}"
    while (( attempts > 0 )); do
        local not_ready total
        not_ready=$(kubectl get pod "$pod" \
            -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null \
            | tr ' ' '\n' | grep -c "false" || true)
        total=$(kubectl get pod "$pod" \
            -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null \
            | tr ' ' '\n' | wc -l)
        [[ $total -gt 0 && $not_ready -eq 0 ]] && return 0
        sleep 3
        (( attempts-- ))
    done
    return 1
}

echo "--- STARTING VOCTOMIX SERVER (CAMERAS IN BLACK) ---"

log "Cleaning up previous session..."
pkill -f "kubectl port-forward" 2>/dev/null || true

if is_minikube_ready && is_studio_ready; then
    log "Cluster and pods already running — skipping startup."
else
    if ! is_minikube_ready; then
        log "Starting minikube..."
        minikube start
    else
        log "Minikube already running."
    fi

    log "Deploying services..."
    export VOCTOMIX_IMAGE="${VOCTOMIX_IMAGE:-martin1210235/voctomix:latest}"
    kubectl apply -f "$BASE_DIR/k8s/configmap.yaml" -f "$BASE_DIR/k8s/secret.yaml" \
        -f "$BASE_DIR/k8s/pvc.yaml" -f "$BASE_DIR/k8s/rabbitmq.yaml" > /dev/null
    envsubst < "$BASE_DIR/k8s/studio.yaml" | kubectl apply -f - > /dev/null

    log "Waiting for RabbitMQ..."
    kubectl wait --for=condition=ready pod -l app=rabbitmq --timeout=120s > /dev/null 2>&1 \
        || { log "RabbitMQ did not start. Check: kubectl logs deployment/rabbitmq"; exit 1; }
    log "RabbitMQ is operational."

    POD=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
    if [[ -z "$POD" ]]; then
        log "Waiting for studio pod to start..."
        kubectl wait --for=condition=ready pod -l app=studio --timeout=180s > /dev/null 2>&1 \
            || { log "Studio pod did not start. Check: kubectl logs deployment/studio -c voctocore"; exit 1; }
    fi

    POD=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if ! wait_for_ready "$POD" 40; then
        log "Studio did not reach ready state. Check: kubectl get pods"
        exit 1
    fi
    log "Studio is operational."
fi

# Replace all camera sources with black frames
log "Setting all cameras to black..."
inject_black cam1  10000
inject_black cam2  10001
inject_black cam3  10002
inject_black cam4  10003
inject_black break 10004
inject_black intro 10005
log "All cameras set to black. Use inject_cam.sh to activate them."

POD=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

log "Exposing ports to the network (accessible from PC 2)..."
kubectl port-forward pod/$POD --address 0.0.0.0 \
    9999:9999 9998:9998 11000:11000 12000:12000 15000:15000 \
    14000:14000 14001:14001 14002:14002 \
    14003:14003 14004:14004 14005:14005 > /tmp/voctomix-pf.log 2>&1 &
PF_PID=$!

for i in $(seq 1 15); do
    sleep 1
    grep -q "Forwarding from" /tmp/voctomix-pf.log 2>/dev/null && break
    kill -0 $PF_PID 2>/dev/null || { log "Port-forward failed."; cat /tmp/voctomix-pf.log; exit 1; }
done

PC1_IP=$(hostname -I | awk '{print $1}')
log "Server running. PC 2 must connect to: $PC1_IP"
echo "--------------------------------------------------------"
log "To activate a camera: inject_cam.sh cam1 /path/to/video.mp4"
log "(Press Ctrl+C to stop the server)"
echo "--------------------------------------------------------"

kubectl logs -f pod/$POD -c telemetry --since=1s 2>/dev/null
