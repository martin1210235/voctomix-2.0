#!/usr/bin/env bash
# Launches the studio configured for the paper Figure 3 screenshot.
#
# Every camera feed shows a different scene of the Big Buck Bunny open test
# sequence (Blender Foundation, CC BY 3.0), so the published figure contains no
# identifiable persons, as required by the MDPI research-ethics policy. The
# repository configuration is left untouched: voctocore reads an extra ini
# passed with -i.
#
# Usage:
#   tools/paper_screenshot/launch_paper_screenshot.sh          # start
#   tools/paper_screenshot/launch_paper_screenshot.sh down     # stop everything
set -u

MODE="${1:-start}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
INI="$ROOT/tools/paper_screenshot/voctocore-paper.ini"
MASTER="$ROOT/videos/bbb_sunflower_2160p_60fps_normal.mp4"
WIDTH=1920; HEIGHT=1080; FRAMERATE=25; AUDIORATE=48000
TAG=voctopaper

# Four visually distinct Big Buck Bunny scenes, one per camera, so the previews
# never show the same frame. Each is cut into its own short clip that the feed
# loops indefinitely: seeking into the master instead would let the live feeds
# drift into the end credits after a few minutes.
#   cam1 -> open meadow (feeds the program view)   cam2 -> brook and flowers
#   cam3 -> squirrels on the branch                cam4 -> forest floor
CLIP_DIR="$ROOT/videos/paper_screenshot"
CLIP_LEN=60
cam_start() {
    case "$1" in
        1) echo 85  ;;
        2) echo 15  ;;
        3) echo 150 ;;
        4) echo 300 ;;
    esac
}

ensure_clips() {
    mkdir -p "$CLIP_DIR"
    for n in 1 2 3 4; do
        local clip="$CLIP_DIR/cam$n.mp4"
        [ -s "$clip" ] && continue
        echo "      building cam$n clip (one-time)..."
        ffmpeg -y -nostdin -loglevel error -ss "$(cam_start "$n")" -t "$CLIP_LEN" \
            -i "$MASTER" \
            -vf "scale=${WIDTH}:${HEIGHT},fps=$FRAMERATE" \
            -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
            -c:a aac -ar "$AUDIORATE" -ac 2 "$clip" </dev/null >/dev/null 2>&1
        [ -s "$clip" ] || { echo "ERROR: could not build $clip"; exit 1; }
    done
}

teardown() {
    pkill -f "$TAG" 2>/dev/null
    pkill -f "python3 voctogui.py" 2>/dev/null
    pkill -f "python3 voctocore.py" 2>/dev/null
    sleep 2
}

if [ "$MODE" = "down" ]; then
    teardown
    echo "stopped."
    exit 0
fi

[ -f "$MASTER" ] || { echo "ERROR: master clip not found: $MASTER"; exit 1; }

echo "--- PAPER FIGURE 3 SCREENSHOT SETUP ---"
teardown

if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^voctocore$'; then
    echo "ERROR: the Docker voctocore is running; stop it first (make docker-down)"
    exit 1
fi

echo "[1/5] starting voctocore (1080p25, paper overrides)..."
( cd "$ROOT/voctocore" && setsid python3 voctocore.py -i "$INI" \
    </dev/null >/tmp/voctopaper_core.log 2>&1 & )
for _ in $(seq 1 45); do
    ss -lnt 2>/dev/null | grep -q ":9999" && break
    sleep 1
done
ss -lnt 2>/dev/null | grep -q ":9999" || {
    echo "ERROR: voctocore did not open port 9999"
    tail -20 /tmp/voctopaper_core.log
    exit 1
}

echo "[2/5] starting auxiliary sources (break, intro, stream-blanker, audio)..."
setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re \
    -i "$ROOT/videos/SLIDES_video_starting_soon.mp4" -pix_fmt yuv420p \
    -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -metadata comment=${TAG}_sb1 -f matroska tcp://127.0.0.1:17000 \
    </dev/null >/dev/null 2>&1 &
setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re \
    -i "$ROOT/videos/stream_offline.mp4" -pix_fmt yuv420p \
    -s "${WIDTH}x${HEIGHT}" -r "$FRAMERATE" -c:v rawvideo -an \
    -metadata comment=${TAG}_sb2 -f matroska tcp://127.0.0.1:17001 \
    </dev/null >/dev/null 2>&1 &
setsid ffmpeg -hide_banner -nostdin -nostats -loglevel error -re -stream_loop -1 \
    -i "$ROOT/videos/musica_pausa.mp3" -c:a pcm_s16le -ar "$AUDIORATE" -ac 2 -vn \
    -metadata comment=${TAG}_audio -f matroska tcp://127.0.0.1:18000 \
    </dev/null >/dev/null 2>&1 &
for spec in "video_cuenta_regresiva_10s.mp4 10004 break" "intro.mp4 10005 intro"; do
    set -- $spec
    setsid ffmpeg -y -nostdin -loglevel error -stream_loop -1 -i "$ROOT/videos/$1" \
        -f lavfi -i "anullsrc=r=$AUDIORATE:cl=stereo" \
        -filter_complex "[0:v] format=yuv420p,scale=${WIDTH}:${HEIGHT}:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=$AUDIORATE [a]" \
        -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
        -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
        -metadata comment=${TAG}_$3 -f matroska "tcp://127.0.0.1:$2" \
        </dev/null >/dev/null 2>&1 &
done

echo "[3/5] starting the four camera feeds (Big Buck Bunny, distinct scenes)..."
ensure_clips
for n in 1 2 3 4; do
    port=$((9999 + n))
    setsid ffmpeg -y -nostdin -loglevel error -stream_loop -1 -re \
        -i "$CLIP_DIR/cam$n.mp4" -ac 2 \
        -filter_complex "[0:v] format=yuv420p,scale=${WIDTH}:${HEIGHT}:out_range=tv,fps=$FRAMERATE,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [0:a] aresample=$AUDIORATE [a]" \
        -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
        -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
        -metadata comment=${TAG}_cam$n -f matroska "tcp://127.0.0.1:$port" \
        </dev/null >/dev/null 2>&1 &
    echo "      cam$n -> :$port (scene from $(cam_start "$n")s, looping)"
done
sleep 8

echo "[4/5] selecting sources, going live and enabling the lower-third overlay..."
core_send() {
    {
        for cmd in "$@"; do
            printf '%s\r\n' "$cmd"
            sleep 0.3
        done
        sleep 0.5
    } | timeout 10 nc -q1 127.0.0.1 9999 >/dev/null 2>&1
}
core_send 'set_video_a cam1' 'set_video_b cam2' \
          'set_composite_mode fullscreen' 'set_stream_live'

if [ "$MODE" = "nogui" ]; then
    echo "[5/5] skipped (nogui): backend is up, voctogui not started."
    exit 0
fi

echo "[5/5] opening voctogui..."
( cd "$ROOT/voctogui" && PYTHONWARNINGS="ignore::DeprecationWarning" \
    setsid python3 voctogui.py </dev/null >/tmp/voctopaper_gui.log 2>&1 & )
sleep 10

# Re-assert the overlay once the GUI has settled: it restores its own overlay
# state on connect, which would otherwise hide the lower third again.
core_send 'show_overlay true'
sleep 2

echo
echo "Ready. The voctogui window should be on screen, showing four Big Buck"
echo "Bunny feeds and the 'Live Broadcast / Camera Feed 01' lower third."
echo "Take the screenshot, then run:"
echo "  tools/paper_screenshot/launch_paper_screenshot.sh down"
