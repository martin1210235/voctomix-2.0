#!/bin/bash
set -euo pipefail

# Usage: ./inject_cam.sh <container> <video_path>
# Example: ./inject_cam.sh cam1 /opt/voctomix/videos/video1.mp4

CONTAINER="${1:-}"
VIDEO_PATH="${2:-}"

log() { echo "[$(date +%H:%M:%S)] $*"; }

usage() {
    echo "Usage: $0 <container> <video_path>"
    echo ""
    echo "Containers: cam1, cam2, cam3, cam4, break, intro"
    echo "Example:    $0 cam1 /opt/voctomix/videos/video1.mp4"
    exit 1
}

[[ -z "$CONTAINER" || -z "$VIDEO_PATH" ]] && usage

declare -A PORT_MAP=(
    [cam1]=10000
    [cam2]=10001
    [cam3]=10002
    [cam4]=10003
    [break]=10004
    [intro]=10005
)

PORT="${PORT_MAP[$CONTAINER]:-}"
if [[ -z "$PORT" ]]; then
    log "Unknown container: $CONTAINER"
    log "Valid containers: cam1 cam2 cam3 cam4 break intro"
    exit 1
fi

log "Activating $CONTAINER with: $VIDEO_PATH"

kubectl exec deployment/studio -c "$CONTAINER" -- \
    bash -c "pkill ffmpeg 2>/dev/null || true; sleep 0.5; \
    ffmpeg -loglevel error -stream_loop -1 -re \
        -i '$VIDEO_PATH' \
        -pix_fmt yuv420p -s \${WIDTH}x\${HEIGHT} -r \${FRAMERATE} \
        -c:v rawvideo -ar \${AUDIORATE} -ac 2 -c:a pcm_s16le \
        -f matroska tcp://localhost:$PORT > /dev/null 2>&1 &"

log "$CONTAINER is now streaming $VIDEO_PATH"
