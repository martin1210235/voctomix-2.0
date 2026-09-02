#!/usr/bin/env bash
# Disambiguates WHERE the frame repetition observed at the heavier profiles comes
# from: the compositor itself, or the synthetic ingest used by the test harness.
#
# In the realistic ("experiment") profile each of the four cameras decodes the
# Big Buck Bunny 4K60 master and rescales it, so at 2160p50 the ingest alone
# costs four simultaneous 4K H.264 decodes plus four rescales on the same host
# that runs the mixer. This script keeps everything else identical and replaces
# only the four camera feeds with lavfi "testsrc2", which is synthesised rather
# than decoded (cheap) yet changes on every frame (so duplicate detection stays
# meaningful, which a solid-colour source would not).
#
# If the programme output becomes frame-fresh under testsrc2, the repetition seen
# with the realistic ingest is attributable to source decoding, not to the
# compositing pipeline.
#
# Usage: ./isolate_source_cost.sh <format> [window_s]

set -u

FMT="${1:?format required, e.g. 2160p50}"
WIN="${2:-15}"

STACK_ROOT="/home/sonda/Documentos/voctomix"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS="${SELF_DIR}/output_integrity_results"
COMP="${STACK_ROOT}/experiments/comprehensive"
TAG=voctosynth

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
}
trap cleanup EXIT

echo "[*] ${FMT}: voctocore + support sources (same as the realistic run)"
bash "${COMP}/set_format.sh" "${FMT}" >/dev/null 2>&1
bash "${COMP}/local_scenario.sh" down >/dev/null 2>&1
bash "${COMP}/local_scenario.sh" base_up >/dev/null 2>&1

echo "[*] starting four synthetic cameras (testsrc2, no decoding)"
for n in 1 2 3 4; do
    port=$((9999 + n))
    setsid ffmpeg -y -nostdin -loglevel error \
        -re -f lavfi -i "testsrc2=size=${W}x${H}:rate=${FPS}" \
        -f lavfi -i "anullsrc=r=48000:cl=stereo" \
        -filter_complex "[0:v] format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; [1:a] aresample=48000 [a]" \
        -map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
        -color_range tv -pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le \
        -metadata comment="${TAG}_cam${n}" -f matroska "tcp://127.0.0.1:${port}" \
        </dev/null >/dev/null 2>&1 &
done

sleep 40
alive=$(pgrep -fc "${TAG}" 2>/dev/null || echo 0)
echo "[*] synthetic cameras alive: ${alive}/4"
if [ "${alive}" -lt 4 ]; then
    echo "[ERROR] synthetic ingest did not start" >&2
    exit 1
fi

(cd "${RESULTS}" && bash "${SELF_DIR}/measure_frame_freshness.sh" \
    "synthetic-src_${FMT}" "${FPS}" "${WIN}")
