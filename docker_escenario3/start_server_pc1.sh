#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

HOST_IP="${HOST_IP:-$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')}"
HOST_IP="${HOST_IP:-$(hostname -I 2>/dev/null | awk '{print $1}')}"
HOST_IP="${HOST_IP:-127.0.0.1}"
export HOST_IP

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

# --- CLEANUP FUNCTION ---
cleanup() {
    log "Server shutdown detected. Stopping containers..."
    cd "$BASE_DIR"
    sudo docker compose down --remove-orphans 2>/dev/null || true
    log "System stopped and resources released."
}
trap cleanup EXIT INT TERM

echo "--- STARTING VOCTOMIX SERVER IN DOCKER (PC 1) ---"

log "Cleaning up previous containers..."
cd "$BASE_DIR"
sudo docker compose down --remove-orphans > /dev/null 2>&1 || true

log "Starting infrastructure (voctocore, cameras, telemetry service)..."
sudo docker compose up -d

log "Server running. Showing telemetry..."
echo "--------------------------------------------------------"
# This script stays alive streaming logs until Ctrl+C is pressed
sudo docker compose logs -f --no-log-prefix telemetry
