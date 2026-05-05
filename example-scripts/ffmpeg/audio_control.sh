#!/bin/bash

# Locate the background music file (two levels up from the script directory)
BACKGROUND_MUSIC="$(cd "$(dirname "$0")/../.." && pwd)/videos/musica_pausa.mp3"

echo "[AUDIO-ONLY] Injecting background music on port 18000..."

# Launch ffmpeg in an infinite loop
# -re: real-time playback rate
# -stream_loop -1: infinite loop
# -vn: disable video (audio only)
ffmpeg -nostats -loglevel warning -re -stream_loop -1 -i "$BACKGROUND_MUSIC" \
    -c:a pcm_s16le -ar 48000 -ac 2 -vn \
    -f matroska tcp://127.0.0.1:18000

# No '&' needed: the container stays alive as long as this process runs.
