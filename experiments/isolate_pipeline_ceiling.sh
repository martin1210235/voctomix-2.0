#!/usr/bin/env bash
# Establishes whether the frame repetition observed at the heavier profiles is
# imposed by the compositing pipeline or merely by the cost of producing the test
# sources on the same host.
#
# Two earlier attempts were inconclusive because both candidate ingests were
# themselves expensive at 4K: decoding the Big Buck Bunny 4K60 master, and
# synthesising lavfi "testsrc2" (a single 2160p50 generator sustains only ~3.3x
# real time on this workstation, so four concurrent instances cannot hold 1x).
#
# This script removes source production from the equation altogether: a short
# clip of already-raw frames is rendered once into /dev/shm, and each camera then
# streams it with "-c copy", so ingest degenerates into a memory read plus a TCP
# write, with no codec and no frame synthesis. The frames still differ from one
# another, so duplicate detection stays meaningful.
#
# If the programme output is still frame-stale under this near-zero-cost ingest,
# the ceiling belongs to the mixing pipeline itself; if it becomes fresh, the
# ceiling was the source simulation.
#
# Usage: ./isolate_pipeline_ceiling.sh <format> [window_s]

set -u

FMT="${1:?format required, e.g. 2160p50}"
WIN="${2:-15}"

STACK_ROOT="/home/sonda/Documentos/voctomix"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS="${SELF_DIR}/output_integrity_results"
COMP="${STACK_ROOT}/experiments/comprehensive"
TAG=voctoraw
SRC="/dev/shm/rawsrc_${FMT}.mkv"
LOOP_S=2

case "${FMT}" in
    1080p25) W=1920; H=1080; FPS=25 ;;
    1080p50) W=1920; H=1080; FPS=50 ;;
    2160p25) W=3840; H=2160; FPS=25 ;;
    2160p50) W=3840; H=2160; FPS=50 ;;
    *) echo "invalid format: ${FMT}" >&2; exit 1 ;;
esac

mkdir -p "${RESULTS}"

cleanup() {
    pkill -f "${TAG}" 2>/dev/null
    bash "${COMP}/local_scenario.sh" down >/dev/null 2>&1
    rm -f "${SRC}"
}
trap cleanup EXIT

echo "[*] pre-rendering ${LOOP_S}s of raw ${FMT} frames into RAM ..."
ffmpeg -y -hide_banner -loglevel error \
    -f lavfi -i "testsrc2=size=${W}x${H}:rate=${FPS}" \
    -f lavfi -i "anullsrc=r=48000:cl=stereo" \
    -t "${LOOP_S}" \
    -filter_complex "[0:v] format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=48000 [a]" \
    -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
    -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
    -f matroska "${SRC}"
echo "[*] source clip: $(du -h "${SRC}" | cut -f1)"

echo "[*] starting voctocore + support sources"
bash "${COMP}/set_format.sh" "${FMT}" >/dev/null 2>&1
bash "${COMP}/local_scenario.sh" down >/dev/null 2>&1
bash "${COMP}/local_scenario.sh" base_up >/dev/null 2>&1

echo "[*] starting four copy-only cameras (no codec, no synthesis)"
for n in 1 2 3 4; do
    port=$((9999 + n))
    setsid ffmpeg -y -nostdin -loglevel error -re -stream_loop -1 -i "${SRC}" \
        -c copy -metadata comment="${TAG}_cam${n}" \
        -f matroska "tcp://127.0.0.1:${port}" \
        </dev/null >/dev/null 2>&1 &
done

sleep 40
alive=$(pgrep -fc "${TAG}" 2>/dev/null || echo 0)
echo "[*] copy-only cameras alive: ${alive}/4"
[ "${alive}" -lt 4 ] && { echo "[ERROR] ingest did not start" >&2; exit 1; }

(cd "${RESULTS}" && bash "${SELF_DIR}/measure_frame_freshness.sh" \
    "rawsrc_${FMT}" "${FPS}" "${WIN}")
