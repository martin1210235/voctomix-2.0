#!/bin/bash

# This script runs in an infinite loop to keep the intro source pre-loaded.
while true; do
    echo "Waiting for the INTRO button to be pressed..."

    # ffmpeg connects to port 10005 and waits for voctocore to accept the connection.
    # As soon as the operator selects INTRO in the GUI, voctocore opens the port,
    # ffmpeg connects and the video starts playing from the very beginning.
    ffmpeg -re -i "$(cd "$(dirname "$0")/../.." && pwd)/videos/intro.mp4" \
    -f lavfi -i anullsrc=r=48000:cl=stereo -pix_fmt yuv420p \
    -s 1920x1080 -r 25 -c:v rawvideo -c:a pcm_s16le \
    -map 0:v:0 -map 1:a:0 -shortest -f matroska tcp://127.0.0.1:10005

    # When the video ends ffmpeg exits and the loop restarts,
    # keeping the source ready for the next time INTRO is selected.
    sleep 1
done
