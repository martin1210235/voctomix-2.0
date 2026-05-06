#!/bin/bash
set -euo pipefail

# --- LOCAL IP AUTO-DETECTION ---
# Uses the real outgoing interface (LAN), not loopback.
# Can be overridden: IP_LOCAL=10.0.0.5 ./arrancar_voctocore_pc1.sh
IP_LOCAL="${IP_LOCAL:-$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')}"
IP_LOCAL="${IP_LOCAL:-$(hostname -I 2>/dev/null | awk '{print $1}')}"
IP_LOCAL="${IP_LOCAL:-127.0.0.1}"

# --- PATH CONFIGURATION ---
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PAUSE_VIDEO="$BASE_DIR/videos/SLIDES_video_starting_soon.mp4"
OFFLINE_VIDEO="$BASE_DIR/videos/stream_offline.mp4"
BACKGROUND_MUSIC="$BASE_DIR/videos/musica_pausa.mp3"
CAM_SCRIPTS="$BASE_DIR/example-scripts/ffmpeg"

export PYTHONWARNINGS="ignore::DeprecationWarning"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

# --- CLEANUP OF PREVIOUS PROCESSES ---
log "Cleaning up previous processes..."
pkill -f "voctocore.py" 2>/dev/null || true
pkill -f "telemetry_service.py"   2>/dev/null || true
pkill -f "ffmpeg.*1700" 2>/dev/null || true
pkill -f "ffmpeg.*1800" 2>/dev/null || true
pkill -f "ffmpeg.*source-testvideo" 2>/dev/null || true
pkill -f "auto_launch_intro" 2>/dev/null || true
pkill -f "tcp://.*:10005" 2>/dev/null || true
# Release port 8080 in case it was left occupied (prevents OSError in the Telemetry Service)
fuser -k 8080/tcp 2>/dev/null || true
sleep 1

# --- CLEANUP FUNCTION ---
cleanup() {
    log "Shutting down the server and releasing ports..."
    jobs -p | xargs -r kill 2>/dev/null || true
    sleep 1
    jobs -p | xargs -r kill -9 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- ACTIVE PORT WAIT ---
wait_for_port() {
    local port="$1"
    local attempts="${2:-20}"
    log "Waiting for port $port..."
    while (( attempts > 0 )); do
        if ss -lnt | awk '{print $4}' | grep -q ":${port}$"; then
            return 0
        fi
        sleep 1
        (( attempts-- ))
    done
    log "Timed out waiting for port $port"
    return 1
}

echo "--- STARTING VOCTOCORE SERVER AT $IP_LOCAL ---"

# 1. Launch voctocore
log "Launching voctocore..."
python3 "$BASE_DIR/voctocore/voctocore.py" 2> >(grep -v "Broken pipe" >&2) &

if ! wait_for_port 9999; then
    log "voctocore did not start correctly. Aborting."
    exit 1
fi
log "voctocore started"

# 2. Launch continuity and VTR sources
log "Launching continuity and VTR sources..."
WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FRAMERATE="${FRAMERATE:-25}"
AUDIORATE="${AUDIORATE:-48000}"

ffmpeg -hide_banner -nostdin -nostats -loglevel error \
    -stream_loop -1 -re -i "$PAUSE_VIDEO" \
    -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -f matroska tcp://127.0.0.1:17000 > /dev/null 2>&1 &

ffmpeg -hide_banner -nostdin -nostats -loglevel error \
    -stream_loop -1 -re -i "$OFFLINE_VIDEO" \
    -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -f matroska tcp://127.0.0.1:17001 > /dev/null 2>&1 &

ffmpeg -hide_banner -nostdin -nostats -loglevel error \
    -re -stream_loop -1 -i "$BACKGROUND_MUSIC" \
    -c:a pcm_s16le -ar "$AUDIORATE" -ac 2 -vn \
    -f matroska tcp://127.0.0.1:18000 > /dev/null 2>&1 &

# 3. Launch camera sources
log "Launching camera sources..."
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam1.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam2.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam3.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam4.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-break.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/auto_launch_intro.sh" > /dev/null 2>&1 &

# 4. Launch Telemetry Service (network HTTP mode)
log "Starting Telemetry Service in network mode (listening on HTTP port 8080)..."
export TELEMETRY_USE_UDP="1"
python3 "$CAM_SCRIPTS/telemetry_service.py" &

log "Server running. Waiting for the operator to connect..."
wait
