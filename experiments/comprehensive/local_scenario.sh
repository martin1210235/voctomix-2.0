#!/usr/bin/env bash
# Manager for the LOCAL scenario (native, no Docker): voctocore + support sources
# + cameras, as host processes. Reuses the same camera ffmpeg commands
# validated on Docker (BBB with markers / solid colour), but native.
#
# IMPORTANTE: todos los procesos de larga vida se lanzan con `setsid ... </dev/null`
# para que se DESLIGUEN por completo. Si no, al llamar a este script con captura de
# output (subprocess), they would inherit the pipe and hang the caller.
#
# Uso:
#   local_scenario.sh base_up            -> voctocore + support (no cameras)
#   local_scenario.sh cam_up <N> <cfg>   -> starts camera N (cfg = experiment|latency)
#   local_scenario.sh crash <N>          -> kills camera N (simulates a failure)
#   local_scenario.sh down               -> mata todo lo nativo
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
SELF="$ROOT/experiments/comprehensive/local_scenario.sh"
MASTER="$ROOT/videos/bbb_sunflower_2160p_60fps_normal.mp4"

[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
WIDTH="${WIDTH:-1920}"; HEIGHT="${HEIGHT:-1080}"; FRAMERATE="${FRAMERATE:-25}"; AUDIORATE="${AUDIORATE:-48000}"

cam_params() {
    case "$1" in
        1) OFFSET=0;   COLOR=red;    HEX=0xFF0000; PORT=10000 ;;
        2) OFFSET=150; COLOR=lime;   HEX=0x00FF00; PORT=10001 ;;
        3) OFFSET=300; COLOR=blue;   HEX=0x0000FF; PORT=10002 ;;
        4) OFFSET=450; COLOR=yellow; HEX=0xFFFF00; PORT=10003 ;;
        *) echo "invalid cam $1" >&2; return 1 ;;
    esac
}

start_cam() {  # $1=N $2=cfg
    cam_params "$1" || return 1
    local tag="voctolocal_cam$1"
    if [ "$2" = "latency" ]; then
        setsid ffmpeg -y -nostdin -loglevel error \
            -f lavfi -i "color=c=$HEX:s=${WIDTH}x${HEIGHT}:r=$FRAMERATE" \
            -f lavfi -i "anullsrc=r=$AUDIORATE:cl=stereo" \
            -filter_complex "[0:v] format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=$AUDIORATE [a]" \
            -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
            -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
            -metadata comment="$tag" -f matroska "tcp://127.0.0.1:$PORT" </dev/null >/dev/null 2>&1 &
    else
        setsid ffmpeg -y -nostdin -loglevel error -stream_loop -1 -ss "$OFFSET" -i "$MASTER" -ac 2 \
            -filter_complex "[0:v] format=yuv420p,scale=${WIDTH}:${HEIGHT}:out_range=tv,fps=$FRAMERATE,drawbox=x=0:y=0:w=iw:h=ih:color=$COLOR:t=40,drawbox=x=0:y=0:w=300:h=300:color=$COLOR:t=fill,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [0:a] aresample=$AUDIORATE [a]" \
            -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
            -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
            -metadata comment="$tag" -f matroska "tcp://127.0.0.1:$PORT" </dev/null >/dev/null 2>&1 &
    fi
    echo "  cam$1 ($2) lanzada -> :$PORT"
}

case "${1:-}" in
  base_up)
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^voctocore$'; then
        echo "ERROR: the Docker voctocore is running; not starting Local"; exit 1
    fi
    pkill -f "voctolocal_" 2>/dev/null
    pkill -f "python3 voctocore.py" 2>/dev/null
    sleep 2
    # voctocore nativo (desligado con setsid)
    ( cd "$ROOT/voctocore" && setsid python3 voctocore.py </dev/null >/tmp/voctolocal_core.log 2>&1 & )
    for i in $(seq 1 45); do ss -lnt 2>/dev/null | grep -q ":9999" && break; sleep 1; done
    ss -lnt 2>/dev/null | grep -q ":9999" || { echo "ERROR: native voctocore did not open port 9999"; tail -5 /tmp/voctolocal_core.log 2>/dev/null; exit 1; }
    # fuentes de soporte (stream-blanker, audio, break, intro), todas desligadas
    setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re -i "$ROOT/videos/SLIDES_video_starting_soon.mp4" -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an -metadata comment=voctolocal_sb1 -f matroska tcp://127.0.0.1:17000 </dev/null >/dev/null 2>&1 &
    setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re -i "$ROOT/videos/stream_offline.mp4" -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an -metadata comment=voctolocal_sb2 -f matroska tcp://127.0.0.1:17001 </dev/null >/dev/null 2>&1 &
    setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -re -stream_loop -1 -i "$ROOT/videos/musica_pausa.mp3" -c:a pcm_s16le -ar "$AUDIORATE" -ac 2 -vn -metadata comment=voctolocal_audio -f matroska tcp://127.0.0.1:18000 </dev/null >/dev/null 2>&1 &
    setsid ffmpeg -y -nostdin -loglevel error -stream_loop -1 -i "$ROOT/videos/video_cuenta_regresiva_10s.mp4" -f lavfi -i "anullsrc=r=$AUDIORATE:cl=stereo" -filter_complex "[0:v] format=yuv420p,scale=${WIDTH}:${HEIGHT}:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=$AUDIORATE [a]" -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le -metadata comment=voctolocal_break -f matroska tcp://127.0.0.1:10004 </dev/null >/dev/null 2>&1 &
    setsid ffmpeg -y -nostdin -loglevel error -stream_loop -1 -i "$ROOT/videos/intro.mp4" -f lavfi -i "anullsrc=r=$AUDIORATE:cl=stereo" -filter_complex "[0:v] format=yuv420p,scale=${WIDTH}:${HEIGHT}:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=$AUDIORATE [a]" -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le -metadata comment=voctolocal_intro -f matroska tcp://127.0.0.1:10005 </dev/null >/dev/null 2>&1 &
    sleep 3
    echo "base_up OK (voctocore + support cameras)"
    ;;
  cam_up)  start_cam "${2:?N}" "${3:?cfg}" ;;
  crash)
    N="${2:?N}"; cam_params "$N" || exit 1
    CFG="${3:-experiment}"
    # Emulate a native process supervisor (systemd Restart=always): the source is
    # killed and a detached watchdog respawns it after RESTART_SEC. The restarted
    # ffmpeg reconnects to voctocore, the same recovery path as Docker's restart policy.
    pkill -9 -f "voctolocal_cam${N}" 2>/dev/null
    setsid bash -c "sleep ${RESTART_SEC:-0.3}; exec bash '$SELF' cam_up '$N' '$CFG'" </dev/null >/dev/null 2>&1 &
    echo "  cam$N matada (supervisor reinicia en ${RESTART_SEC:-0.3}s)"
    ;;
  down)
    pkill -f "voctolocal_" 2>/dev/null
    pkill -f "python3 voctocore.py" 2>/dev/null
    sleep 2; echo "down OK"
    ;;
  *) echo "uso: local_scenario.sh base_up|cam_up N cfg|crash N|down" >&2; exit 1 ;;
esac
