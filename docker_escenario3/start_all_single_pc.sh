#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Shutting down local studio..."
    pkill -f "ffplay .*15000" 2>/dev/null || true
    pkill -f "python3 voctogui.py" 2>/dev/null || true
    cd "$BASE_DIR"
    sudo docker compose down > /dev/null 2>&1 || true
    log "Studio closed and containers stopped."
}
trap cleanup EXIT INT TERM

wait_for_healthy() {
    local service="$1"
    local attempts="${2:-30}"
    log "Waiting for '$service' to become healthy..."
    while (( attempts > 0 )); do
        status=$(sudo docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "not-found")
        if [[ "$status" == "healthy" ]]; then
            return 0
        fi
        sleep 2
        (( attempts-- ))
    done
    log "'$service' did not reach healthy state (last status: $status)"
    return 1
}

echo "--- STARTING VOCTOMIX STUDIO (SINGLE PC) ---"

log "Cleaning up containers and previous viewers..."
cd "$BASE_DIR"
sudo docker compose down > /dev/null 2>&1 || true
pkill -f "ffplay .*15000" 2>/dev/null || true

log "Starting infrastructure in the background (Docker)..."
sudo docker compose up -d

if ! wait_for_healthy "voctocore" 30; then
    log "voctocore did not start. Check: sudo docker compose logs voctocore"
    exit 1
fi
log "voctocore is operational"

log "Opening local PROGRAM monitor..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" \
    tcp://127.0.0.1:15000 > /dev/null 2>&1 &

log "Opening voctogui..."
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py 2>/dev/null &

log "System live and ready."
echo "--------------------------------------------------------"
log "Showing telemetry service logs..."
log "(Press Ctrl+C to shut down the entire studio)"
echo "--------------------------------------------------------"

cd "$BASE_DIR"
sudo docker compose logs -f telemetry
