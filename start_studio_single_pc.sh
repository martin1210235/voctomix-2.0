#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PAUSE_VIDEO="$BASE_DIR/videos/SLIDES_video_starting_soon.mp4"
OFFLINE_VIDEO="$BASE_DIR/videos/stream_offline.mp4"
BACKGROUND_MUSIC="$BASE_DIR/videos/musica_pausa.mp3"
CAM_SCRIPTS="$BASE_DIR/example-scripts/ffmpeg"

log() {
    echo "[$(date +%H:%M:%S)] $*"
}

cleanup() {
    log "Shutting down..."
    jobs -p | xargs -r kill 2>/dev/null || true
    sleep 1
    jobs -p | xargs -r kill -9 2>/dev/null || true
    pkill -f "ffplay .*11000" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

kill_previous() {
    log "Cleaning up previous processes..."
    pkill -f "python3 voctocore.py" 2>/dev/null || true
    pkill -f "python3 voctogui.py" 2>/dev/null || true
    pkill -f "python3 .*telemetry_service.py" 2>/dev/null || true
    pkill -f "ffplay .*11000" 2>/dev/null || true
    pkill -f "tcp://127.0.0.1:17000" 2>/dev/null || true
    pkill -f "tcp://127.0.0.1:17001" 2>/dev/null || true
    pkill -f "tcp://127.0.0.1:18000" 2>/dev/null || true
    pkill -f "tcp://localhost:10000" 2>/dev/null || true
    pkill -f "tcp://localhost:10001" 2>/dev/null || true
    pkill -f "tcp://localhost:10002" 2>/dev/null || true
    pkill -f "tcp://localhost:10003" 2>/dev/null || true
    pkill -f "tcp://localhost:10004" 2>/dev/null || true
    pkill -f "tcp://localhost:10005" 2>/dev/null || true
    sleep 2
}

wait_for_port() {
    local port="$1"
    local attempts=20
    while (( attempts > 0 )); do
        if ss -lnt | awk '{print $4}' | grep -q ":${port}$"; then
            return 0
        fi
        sleep 1
        ((attempts--))
    done
    return 1
}

echo "--- STARTING STUDIO (SINGLE PC) ---"

kill_previous

log "Starting voctocore..."
cd "$BASE_DIR/voctocore"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctocore.py > /dev/null 2>&1 &

if ! wait_for_port 9999; then
    log "voctocore did not start correctly. Aborting."
    exit 1
fi
log "voctocore started"

WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FRAMERATE="${FRAMERATE:-25}"
AUDIORATE="${AUDIORATE:-48000}"

log "Starting continuity and VTR sources..."
ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re \
    -i "$PAUSE_VIDEO" \
    -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -f matroska tcp://127.0.0.1:17000 > /dev/null 2>&1 &

ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re \
    -i "$OFFLINE_VIDEO" \
    -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -f matroska tcp://127.0.0.1:17001 > /dev/null 2>&1 &

ffmpeg -hide_banner -nostdin -nostats -loglevel error -re -stream_loop -1 \
    -i "$BACKGROUND_MUSIC" \
    -c:a pcm_s16le -ar "$AUDIORATE" -ac 2 -vn \
    -f matroska tcp://127.0.0.1:18000 > /dev/null 2>&1 &

log "Starting camera sources..."
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam1.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam2.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam3.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-cam4.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/source-testvideo-as-break.sh" > /dev/null 2>&1 &
/bin/bash "$CAM_SCRIPTS/auto_launch_intro.sh" > /dev/null 2>&1 &

log "Starting telemetry service..."
python3 "$CAM_SCRIPTS/telemetry_service.py" &

sleep 2

log "Opening PROGRAM monitor..."
ffplay -hide_banner -loglevel error -window_title "PROGRAM" tcp://127.0.0.1:15000 > /dev/null 2>&1 &

sleep 1

log "Starting voctogui..."
cd "$BASE_DIR/voctogui"
PYTHONWARNINGS="ignore::DeprecationWarning" python3 voctogui.py 2>/dev/null || true
