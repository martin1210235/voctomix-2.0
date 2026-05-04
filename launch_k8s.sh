#!/bin/bash
set -euo pipefail

export MINIKUBE_IN_STYLE=false
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

log() {
    echo "[$(date +%H:%M:%S)] $*"
    echo ""
}

cleanup() {
    log "Shutting down studio..."
    pkill -f "voctogui.py" 2>/dev/null || true
    kill $PF_PID 2>/dev/null || true
    kill $LOG_PID 2>/dev/null || true
    log "Studio closed."
}
trap cleanup EXIT INT TERM

wait_for_ready() {
    local pod="$1"
    local attempts="${2:-40}"
    log "Waiting for studio pod to be ready..."
    while (( attempts > 0 )); do
        ready=$(kubectl get pod "$pod" \
            -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null || echo "")
        not_ready=$(echo "$ready" | tr ' ' '\n' | grep -c "false" || true)
        total=$(echo "$ready" | tr ' ' '\n' | wc -l)
        if [[ $total -gt 0 && $not_ready -eq 0 ]]; then
            return 0
        fi
        sleep 3
        (( attempts-- ))
    done
    log "Studio pod did not become ready in time."
    return 1
}

echo "--- STARTING VOCTOMIX STUDIO (Kubernetes) ---"

log "Cleaning up previous session..."
pkill -f "kubectl port-forward" 2>/dev/null || true
pkill -f "voctogui.py" 2>/dev/null || true

log "Starting minikube..."
minikube start

log "Deploying services..."
kubectl apply -f "$BASE_DIR/k8s/" > /dev/null

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
    POD=$(kubectl get pod -l app=studio --field-selector=status.phase=Running \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

if ! wait_for_ready "$POD" 40; then
    log "Studio did not reach ready state. Check: kubectl get pods"
    exit 1
fi
log "Studio is operational."

log "Setting up port-forward..."
kubectl port-forward pod/$POD \
    9999:9999 9998:9998 11000:11000 12000:12000 \
    14000:14000 14001:14001 14002:14002 \
    14003:14003 14004:14004 14005:14005 > /tmp/voctomix-pf.log 2>&1 &
PF_PID=$!

for i in $(seq 1 15); do
    sleep 1
    if grep -q "Forwarding from" /tmp/voctomix-pf.log 2>/dev/null; then
        break
    fi
    if ! kill -0 $PF_PID 2>/dev/null; then
        log "Port-forward failed. Check /tmp/voctomix-pf.log"
        cat /tmp/voctomix-pf.log
        exit 1
    fi
done
log "Port-forward ready."

log "Opening voctogui..."
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py -H localhost 2>/dev/null &
GUI_PID=$!

log "System live and ready."
echo "--------------------------------------------------------"
log "Showing telemetry logs..."
log "(Press Ctrl+C to shut down the studio and close the GUI)"
echo "--------------------------------------------------------"

kubectl logs -f pod/$POD -c telemetry --since=1s 2>/dev/null &
LOG_PID=$!

wait $GUI_PID 2>/dev/null || true
