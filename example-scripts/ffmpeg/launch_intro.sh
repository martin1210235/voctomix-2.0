#!/bin/bash

# voctocore IP: localhost in 1PC mode; in 2PC mode the GUI exports GUI_TARGET_IP.
VOCTOCORE_IP="${GUI_TARGET_IP:-127.0.0.1}"

# Kill any running intro ffmpeg process and wait for voctocore to release the
# socket before connecting a new one. If nothing is running, proceed immediately.
pkill -f "tcp://.*:10005" 2>/dev/null && sleep 0.5

# Play the intro video from the beginning (no -stream_loop = single playback).
# stderr is suppressed to avoid "Broken pipe" messages on normal shutdown.
WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FRAMERATE="${FRAMERATE:-25}"
AUDIORATE="${AUDIORATE:-48000}"
INTRO_PORT="${INTRO_PORT:-10005}"

ffmpeg -loglevel error -nostats -re \
    -i "$(cd "$(dirname "$0")/../.." && pwd)/videos/intro.mp4" \
    -f lavfi -i anullsrc=r=${AUDIORATE}:cl=stereo \
    -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "${FRAMERATE}" \
    -c:v rawvideo -c:a pcm_s16le \
    -map 0:v:0 -map 1:a:0 \
    -shortest \
    -f matroska tcp://"$VOCTOCORE_IP":${INTRO_PORT} 2>/dev/null
