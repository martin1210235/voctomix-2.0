#!/bin/bash
cd "$(dirname ${BASH_SOURCE[0]})"

while true; do
	sleep 10
	echo "composite-pip"
	./set-composite-picture-in-picture.sh
	sleep 10
	echo "audio/video cam2"
	./set-video-cam2.sh
	./set-audio-cam2.sh
	sleep 10
	echo "composite-sbs"
	./set-composite-side-by-side-preview.sh
	sleep 10
	echo "audio/video cam1"
	./set-audio-cam1.sh
	./set-video-cam1.sh
	sleep 10
	echo "composite-fs"
	./set-composite-fullscreen.sh
	sleep 10
	echo "audio/video cam2"
	./set-audio-cam2.sh
	./set-video-cam2.sh
	sleep 10
	echo "audio/video cam1"
	./set-video-cam1.sh
	./set-audio-cam1.sh
	sleep 10
	echo "composite-sbs"
	./set-composite-side-by-side-equal.sh
	sleep 10
	echo "audio/video cam2"
	./set-video-cam2.sh
	./set-audio-cam2.sh
	sleep 10
	echo "composite-pip"
	./set-composite-picture-in-picture.sh
	sleep 10
	echo "audio/video cam1, composite-fs"
	./set-video-cam1.sh
	./set-audio-cam1.sh
	./set-composite-fullscreen.sh
done
