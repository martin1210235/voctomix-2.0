#!/bin/bash

# Paths relative to the repo root (two levels up from example-scripts/ffmpeg)
PAUSE_VIDEO="$(cd "$(dirname "$0")/../.." && pwd)/videos/SLIDES_video_starting_soon.mp4"
OFFLINE_VIDEO="$(cd "$(dirname "$0")/../.." && pwd)/videos/stream_offline.mp4"
BACKGROUND_MUSIC="$(cd "$(dirname "$0")/../.." && pwd)/videos/musica_pausa.mp3"

echo "Starting Voctomix continuity sources..."

# 1. Inject PAUSE video -> port 17000
ffmpeg -nostats -loglevel warning -stream_loop -1 -re -i "$PAUSE_VIDEO" -pix_fmt yuv420p -s 1920x1080 -r 25 -c:v rawvideo -an -f matroska tcp://127.0.0.1:17000 &

# 2. Inject NOSTREAM video -> port 17001
ffmpeg -nostats -loglevel warning -stream_loop -1 -re -i "$OFFLINE_VIDEO" -pix_fmt yuv420p -s 1920x1080 -r 25 -c:v rawvideo -an -f matroska tcp://127.0.0.1:17001 &

# 3. Inject background audio -> port 18000
ffmpeg -nostats -loglevel warning -re -stream_loop -1 -i "$BACKGROUND_MUSIC" -c:a pcm_s16le -ar 48000 -ac 2 -vn -f matroska tcp://127.0.0.1:18000 &

echo "All sources injecting in loop."
wait
