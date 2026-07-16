#!/bin/bash
cd "$(dirname ${BASH_SOURCE[0]})"

while true; do
	sleep 10
<<<<<<< HEAD
	echo "composite-picture-in-picture"
=======
	echo "composite-pip"
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
	./set-composite-picture-in-picture.sh
	sleep 10
	echo "audio/video cam2"
	./set-video-cam2.sh
	./set-audio-cam2.sh
	sleep 10
<<<<<<< HEAD
	echo "composite-side-by-side-preview"
=======
	echo "composite-sbs"
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
	./set-composite-side-by-side-preview.sh
	sleep 10
	echo "audio/video cam1"
	./set-audio-cam1.sh
	./set-video-cam1.sh
	sleep 10
<<<<<<< HEAD
	echo "composite-fullscreen"
=======
	echo "composite-fs"
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
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
<<<<<<< HEAD
	echo "composite-side-by-side-equal"
=======
	echo "composite-sbs"
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
	./set-composite-side-by-side-equal.sh
	sleep 10
	echo "audio/video cam2"
	./set-video-cam2.sh
	./set-audio-cam2.sh
	sleep 10
<<<<<<< HEAD
	echo "composite-picture-in-picture"
	./set-composite-picture-in-picture.sh
	sleep 10
	echo "audio/video cam1, composite-fullscreen"
=======
	echo "composite-pip"
	./set-composite-picture-in-picture.sh
	sleep 10
	echo "audio/video cam1, composite-fs"
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
	./set-video-cam1.sh
	./set-audio-cam1.sh
	./set-composite-fullscreen.sh
done
