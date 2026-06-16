#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# IP of PC 1 (Kubernetes server). Defaults to localhost for single-PC use.
#   IP_SERVER=10.0.0.5 ./start_operator_pc2.sh
IP_SERVER="${IP_SERVER:-192.168.0.47}"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Closing operator workstation..."
    pkill -f "voctogui.py" 2>/dev/null || true
    pkill -f "ffplay .*15000" 2>/dev/null || true
    log "Disconnected from server."
}
trap cleanup EXIT INT TERM

wait_for_connection() {
    local host="$1"
    local port="$2"
    local attempts="${3:-30}"
    log "Waiting for connection to $host:$port..."
    while (( attempts > 0 )); do
        nc -zw1 "$host" "$port" 2>/dev/null && return 0
        sleep 1
        (( attempts-- ))
    done
    log "Could not connect to $host:$port"
    return 1
}

echo "--- CONNECTING TO KUBERNETES SERVER ($IP_SERVER) ---"

if ! wait_for_connection "$IP_SERVER" 9999; then
    log "Server not responding at $IP_SERVER:9999. Is PC 1 running start_server_pc1.sh?"
    exit 1
fi
log "voctocore server detected."

log "Opening PROGRAM monitor..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" \
    tcp://"$IP_SERVER":15000 > /dev/null 2>&1 &

log "Opening voctogui..."
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" \
    VOCTOCORE_PORT=9999 VOCTOCORE_CLOCK_PORT=9998 \
    MIX_OUT_PORT=12000 \
    python3 voctogui.py -H "$IP_SERVER" 2>/dev/null
