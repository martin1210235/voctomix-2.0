#!/bin/sh
confdir="`dirname "$0"`/../"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
    . $confdir/config.sh
fi

ffmpeg -y -nostdin -stream_loop -1 \
    -i "https://www.w3schools.com/html/mov_bbb.mp4" \
    -filter_complex "
        [0:v] format=yuv420p,scale=$WIDTH:$HEIGHT:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v] ;
        [0:a] aresample=$AUDIORATE [a]
    " \
    -map "[v]" -map "[a]" \
    -color_primaries bt709 \
    -color_trc bt709 \
    -colorspace bt709 \
    -color_range tv \
    -c:v rawvideo \
    -c:a pcm_s16le \
    -f matroska \
    tcp://localhost:10003
