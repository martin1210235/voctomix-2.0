#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

HOST_IP="${HOST_IP:-$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')}"
HOST_IP="${HOST_IP:-$(hostname -I 2>/dev/null | awk '{print $1}')}"
HOST_IP="${HOST_IP:-127.0.0.1}"
export HOST_IP

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Shutting down studio..."
    pkill -f "python3 voctogui.py" 2>/dev/null || true
    pkill -f "ffplay.*15000" 2>/dev/null || true
    cd "$BASE_DIR"
    sudo docker compose down > /dev/null 2>&1 || true
    log "Studio closed."
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
    log "'$service' did not reach healthy state in time (last status: $status)"
    return 1
}

echo "--- STARTING VOCTOMIX STUDIO ---"

log "Cleaning up previous containers..."
cd "$BASE_DIR"
sudo docker compose down > /dev/null 2>&1 || true

log "Starting infrastructure in the background (Docker)..."
sudo docker compose up -d

if ! wait_for_healthy "voctocore" 30; then
    log "voctocore did not start. Check: sudo docker compose logs voctocore"
    exit 1
fi
log "voctocore is operational"

log "Opening voctogui..."
cd "$BASE_DIR/voctogui"
GUI_TARGET_IP="127.0.0.1" TELEMETRY_HTTP_PORT="8080" \
    PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py 2>/dev/null &

log "Opening program monitor (port 15000)..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" tcp://127.0.0.1:15000 &

log "Opening telemetry logs in a separate window..."
TELEMETRY_LOGS_CMD="cd '$BASE_DIR' && docker compose logs -f telemetry"
# xterm first: OBS XComposite window-capture renders it reliably, while
# GPU-accelerated terminals (gnome-terminal) can appear black in the capture.
if command -v xterm >/dev/null 2>&1; then
    xterm -T "TELEMETRY" -fa "Monospace" -fs 14 -bg black -fg white \
          -geometry 120x30 -e bash -lc "$TELEMETRY_LOGS_CMD" &
elif command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="TELEMETRY" -- bash -lc "$TELEMETRY_LOGS_CMD" &
else
    x-terminal-emulator -e bash -lc "$TELEMETRY_LOGS_CMD" &
fi

log "System live and ready."
echo "--------------------------------------------------------"
log "Telemetry logs are shown in the separate 'TELEMETRY' window."
log "(Press Ctrl+C here to shut down the studio and close the GUI)"
echo "--------------------------------------------------------"

# Keep this terminal alive so the cleanup trap runs on Ctrl+C.
while true; do sleep 3600; done
