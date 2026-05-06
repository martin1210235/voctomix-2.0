#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# IP of PC 1 (server). Must be set before running:
#   IP_SERVER=10.0.0.5 ./start_voctogui_pc2.sh
if [[ -z "${IP_SERVER:-}" ]]; then
    echo "ERROR: IP_SERVER is not set. Usage: IP_SERVER=<server-ip> $0"
    exit 1
fi

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Shutting down operator workstation..."
    pkill -f "ffplay .*15000" 2>/dev/null || true
    # Kill intro ffmpeg process if running (prevents "Broken pipe" messages)
    pkill -f "tcp://.*:10005" 2>/dev/null || true
    jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait_for_connection() {
    local host="$1"
    local port="$2"
    local attempts="${3:-30}"
    log "Waiting for connection to $host:$port..."
    while (( attempts > 0 )); do
        if nc -zw1 "$host" "$port" 2>/dev/null; then
            return 0
        fi
        sleep 1
        (( attempts-- ))
    done
    log "Could not connect to $host:$port"
    return 1
}

echo "--- CONNECTING TO SERVER ($IP_SERVER) ---"

if ! wait_for_connection "$IP_SERVER" 9999; then
    log "Server not responding at $IP_SERVER:9999. Is PC 1 running?"
    exit 1
fi
log "voctocore server detected"

# 1. Connect program monitor to the server IP
log "Opening PROGRAM monitor over the network..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" \
    tcp://"$IP_SERVER":15000 > /dev/null 2>&1 &

# 2. Connect the GUI to the server IP
log "Opening voctogui and connecting telemetry..."
export GUI_TARGET_IP="$IP_SERVER"
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py -H "$IP_SERVER"
