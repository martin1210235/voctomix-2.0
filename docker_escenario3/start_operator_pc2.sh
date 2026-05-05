#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# IP of PC 1 (Docker server). Override if the network address changes:
#   IP_CEREBRO=10.0.0.5 ./start_operator_pc2.sh
IP_CEREBRO="${IP_CEREBRO:-192.168.0.42}"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Closing operator workstation..."
    pkill -f "ffplay .*15000" 2>/dev/null || true
    jobs -p | xargs -r kill 2>/dev/null || true
    log "Disconnected from server."
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

echo "--- CONNECTING TO SERVER ($IP_CEREBRO) ---"

if ! wait_for_connection "$IP_CEREBRO" 9999; then
    log "Docker server not responding at $IP_CEREBRO:9999. Is PC 1 running?"
    exit 1
fi
log "voctocore server detected"

log "Opening PROGRAM monitor over the network..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" \
    tcp://"$IP_CEREBRO":15000 > /dev/null 2>&1 &

log "Opening voctogui and connecting telemetry..."
export GUI_TARGET_IP="$IP_CEREBRO"
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py -H "$IP_CEREBRO" > /dev/null 2>&1
