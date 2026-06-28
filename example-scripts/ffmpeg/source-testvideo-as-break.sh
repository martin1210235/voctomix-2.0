#!/bin/sh
confdir="`dirname "$0"`/../"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
    . $confdir/config.sh
fi

VIDEO_FILE="$(cd "$(dirname "$0")/../.." && pwd)/videos/video_cuenta_regresiva_10s.mp4"
AUDIO_FILE="$(cd "$(dirname "$0")/../.." && pwd)/videos/musica_pausa.mp3"

echo "[BREAK] Injecting break video with background audio..."

ffmpeg -y -nostdin -stream_loop -1 \
    -i "$VIDEO_FILE" \
    -re -stream_loop -1 -i "$AUDIO_FILE" \
    -filter_complex "
        [0:v] format=yuv420p,scale=$WIDTH:$HEIGHT:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v] ;
        [1:a] aresample=$AUDIORATE,pan=stereo|c0=c0|c1=c1 [a]
    " \
    -map "[v]" -map "[a]" \
    -c:v rawvideo \
    -c:a pcm_s16le \
    -f matroska \
    tcp://localhost:10004
