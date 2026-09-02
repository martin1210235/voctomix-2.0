#!/usr/bin/env bash
# Output-integrity measurement for reviewer point R2.1 (frame drop / output fps).
# Counts the frames actually delivered by the compositor over a fixed window and
# derives output fps and drop rate. Run on the test workstation, once the
# corresponding deployment (local / docker / k8s) is up with four active sources.
#
# IMPORTANT: measure the RAW MIX output on port 11000, which is the compositor's
# programme output BEFORE the stream blanker. Port 15000 is the post-blanker
# programme feed and is black unless the blanker is explicitly set to LIVE, so it
# must NOT be used for frame-integrity measurement (see paper/pruebas/RUNBOOK.md).
#
# WHY NOTHING IS WRITTEN TO DISK: the mix is uncompressed I420, i.e. 78 MB/s at
# 1080p25 and 622 MB/s at 2160p50 (a 60 s capture would be 4.7 GB and 37.3 GB
# respectively, and the full campaign several hundred GB). Beyond being
# impractical, a storage backend that cannot keep up would stall the TCP reader,
# and voctocore's multifdsink drops clients it considers too slow, which would be
# recorded as pipeline frame loss that never happened. Frames are therefore
# counted in-flight with "-f null" so the measurement cannot manufacture the very
# effect it is meant to detect.
#
# Host CPU is sampled over the same window (same /proc source as the original
# campaign) so frame integrity can be reported against the load it was measured
# under.
#
# Usage:
#   ./measure_output_integrity.sh <scenario_label> <fps_nominal> [duration_s] [mix_url]
# Example:
#   ./measure_output_integrity.sh docker_1080p25 25 60 tcp://127.0.0.1:11000
#
# Output: appends a CSV row to output_integrity.csv in the current directory.

set -euo pipefail

LABEL="${1:?scenario label required, e.g. docker_1080p25}"
FPS_NOM="${2:?nominal fps required, e.g. 25}"
DUR="${3:-60}"
PROG_URL="${4:-tcp://127.0.0.1:11000}"

OUT_CSV="output_integrity.csv"
FF_LOG="/tmp/integrity_${LABEL}_$$.log"
CPU_OUT="/tmp/integrity_cpu_${LABEL}_$$.txt"

# Count live camera feeds independently of the deployment tier, so every row can
# state how many sources were actually running while it was measured rather than
# relying on a check made once before the block started.
count_sources() {
    # Each branch has to swallow its own failure: grep -c exits non-zero when it
    # matches nothing, and under `set -e` that aborted the whole measurement
    # before the row was ever written.
    local d l k
    d=$( { docker ps --filter health=healthy --format '{{.Names}}' 2>/dev/null \
           | grep -cE '^cam[1-4]$'; } || true )
    l=$( { pgrep -fc 'voctolocal_cam[1-4]' 2>/dev/null; } || true )
    k=$( { kubectl get pods -n voctomix-exp --no-headers 2>/dev/null \
           | grep -E '^cam[1-4]-' | grep -c Running; } || true )
    d=${d:-0}; l=${l:-0}; k=${k:-0}
    echo $(( d > l ? (d > k ? d : k) : (l > k ? l : k) ))
}
SRC_BEFORE=$(count_sources)

# Sample whole-host CPU across the measurement window, from /proc/stat, exactly
# as the original campaign did.
python3 - "$DUR" "$CPU_OUT" <<'PY' &
import sys, time
dur = float(sys.argv[1]); out = sys.argv[2]
def snap():
    with open("/proc/stat") as f:
        v = [float(x) for x in f.readline().split()[1:]]
    return sum(v), v[3] + (v[4] if len(v) > 4 else 0.0)
samples = []
t0, i0 = snap()
end = time.time() + dur
while time.time() < end:
    time.sleep(1)
    t1, i1 = snap()
    dt, di = t1 - t0, i1 - i0
    if dt > 0:
        samples.append(100.0 * (dt - di) / dt)
    t0, i0 = t1, i1
samples.sort()
med = samples[len(samples) // 2] if samples else 0.0
open(out, "w").write(f"{med:.1f}")
PY
CPU_PID=$!

echo "[*] Counting ${DUR}s of delivered frames for '${LABEL}' ..."
# -c copy keeps demuxed packets intact (one packet == one raw frame) and -f null
# discards the payload, so the reader never becomes the bottleneck.
timeout "$((DUR + 30))" ffmpeg -hide_banner -nostdin -i "${PROG_URL}" \
  -t "${DUR}" -c copy -f null - >"${FF_LOG}" 2>&1 || true

SRC_AFTER=$(count_sources)
wait "${CPU_PID}" 2>/dev/null || true
CPU_MED=$(cat "${CPU_OUT}" 2>/dev/null || echo "")

NB_FRAMES=$(grep -oE 'frame=\s*[0-9]+' "${FF_LOG}" | tail -1 | grep -oE '[0-9]+' || true)
if [ -z "${NB_FRAMES}" ] || [ "${NB_FRAMES}" -eq 0 ]; then
  echo "[ERROR] No frames delivered on ${PROG_URL} for '${LABEL}'. Check the stack is up," >&2
  echo "        4 sources active, and the port is 11000 (raw mix), not 15000." >&2
  tail -5 "${FF_LOG}" >&2
  exit 1
fi

# Format is taken from the same connection that counted the frames, so the row
# records the profile that was actually measured.
# The ", WxH" form is required so the pixel-format token (e.g. "/ 0x30323449")
# cannot be mistaken for a resolution.
RES=$(sed -n 's/.*, \([0-9]\{3,5\}x[0-9]\{3,5\}\)[ ,].*/\1/p' "${FF_LOG}" | head -1)
TBR=$(grep -oE '[0-9.]+ tbr' "${FF_LOG}" | head -1 | grep -oE '[0-9.]+' || true)
PROBE="${RES:-unknown}@${TBR:-?}"
PROBE=$(printf '%s' "${PROBE}" | tr -d '\n\r,')
echo "[*] Stream reported: ${PROBE}"

EXPECTED=$(python3 -c "print(int(${DUR} * ${FPS_NOM}))")
python3 - "$LABEL" "$FPS_NOM" "$DUR" "$NB_FRAMES" "$EXPECTED" "$PROBE" "$CPU_MED" "$SRC_BEFORE" "$SRC_AFTER" "$OUT_CSV" <<'PY'
import sys, os
label, fps_nom, dur, nb, exp, probe, cpu, srcb, srca, out = sys.argv[1:11]
nb = int(nb); exp = int(exp); dur = float(dur)
drop = 100.0 * (exp - nb) / exp if exp else 0.0
out_fps = nb / dur if dur else 0.0
header = ("scenario,fps_nominal,duration_s,frames_expected,frames_delivered,"
          "drop_rate_pct,output_fps,stream_format,cpu_pct_median,"
          "sources_before,sources_after\n")
row = (f"{label},{fps_nom},{dur:.0f},{exp},{nb},{drop:.4f},{out_fps:.3f},"
       f"{probe.replace(',', 'x')},{cpu},{srcb},{srca}\n")
newfile = not os.path.exists(out)
with open(out, "a") as fh:
    if newfile:
        fh.write(header)
    fh.write(row)
print(f"[OK] {label}: delivered {nb}/{exp} frames  drop={drop:.4f}%  "
      f"out_fps={out_fps:.3f}  host_cpu={cpu}%  sources={srcb}->{srca}")
PY

rm -f "${FF_LOG}" "${CPU_OUT}"
echo "[*] Appended to ${OUT_CSV}"
