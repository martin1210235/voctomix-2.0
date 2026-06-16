#!/bin/bash
# Injects the continuity video loops for stream blanking

PAUSE_VIDEO="$(cd "$(dirname "$0")/../.." && pwd)/videos/SLIDES_video_starting_soon.mp4"
VIDEO_OFFLINE="$(cd "$(dirname "$0")/../.." && pwd)/videos/stream_offline.mp4"

WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FRAMERATE="${FRAMERATE:-25}"

echo "[VIDEO BLANKER] Starting video injection..."

# 1. Inject PAUSE video -> port 17000
ffmpeg -nostats -loglevel warning -stream_loop -1 -re -i "$PAUSE_VIDEO" -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an -f matroska tcp://127.0.0.1:17000 &

# 2. Inject NOSTREAM video -> port 17001
ffmpeg -nostats -loglevel warning -stream_loop -1 -re -i "$VIDEO_OFFLINE" -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an -f matroska tcp://127.0.0.1:17001 &

echo "Video sources running. Waiting..."
wait
