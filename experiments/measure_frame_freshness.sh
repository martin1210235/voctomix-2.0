#!/usr/bin/env bash
# Frame-freshness check, complementing measure_output_integrity.sh (reviewer R2.1).
#
# WHY THIS EXISTS: counting frames at the programme sink proves the output
# cadence is intact, but not that the content is fresh. A compositor starved by
# its sources can still emit at the nominal rate by repeating the last frame,
# which is precisely the "silently dropping frames" failure the reviewer asks us
# to rule out. This script therefore captures a short window and counts how many
# consecutive frames are exact duplicates (ffmpeg's mpdecimate), so cadence and
# content can be reported separately.
#
# The window is short and written to /dev/shm (RAM) because the raw mix runs at
# 622 MB/s at 2160p50; the analysis is then done offline so it cannot perturb the
# pipeline it is measuring.
#
# Usage:
#   ./measure_frame_freshness.sh <scenario_label> <fps_nominal> [window_s] [mix_url]

set -euo pipefail

LABEL="${1:?scenario label required}"
FPS_NOM="${2:?nominal fps required}"
WIN="${3:-5}"
PROG_URL="${4:-tcp://127.0.0.1:11000}"

OUT_CSV="frame_freshness.csv"
CAP="/dev/shm/freshness_${LABEL}.mkv"

cleanup() { rm -f "${CAP}"; }
trap cleanup EXIT

echo "[*] Capturing ${WIN}s from ${PROG_URL} to RAM for '${LABEL}' ..."
timeout "$((WIN + 40))" ffmpeg -y -hide_banner -loglevel error -nostdin \
  -i "${PROG_URL}" -t "${WIN}" -c copy "${CAP}" || true

if [ ! -s "${CAP}" ]; then
  echo "[ERROR] Empty capture for '${LABEL}'." >&2
  exit 1
fi

TOTAL=$(ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames -of default=nk=1:nw=1 "${CAP}")

# mpdecimate forwards only frames that differ from the previous one, so the
# frame count it reports is the number of visually distinct frames.
UNIQUE=$(ffmpeg -hide_banner -nostdin -i "${CAP}" -vf mpdecimate -f null - 2>&1 \
  | grep -oE 'frame=\s*[0-9]+' | tail -1 | grep -oE '[0-9]+')

python3 - "$LABEL" "$FPS_NOM" "$WIN" "$TOTAL" "$UNIQUE" "$OUT_CSV" <<'PY'
import sys, os
label, fps_nom, win, total, uniq, out = sys.argv[1:7]
total = int(total); uniq = int(uniq); win = float(win)
dup = total - uniq
dup_pct = 100.0 * dup / total if total else 0.0
header = ("scenario,fps_nominal,window_s,frames_total,frames_unique,"
          "duplicate_frames,duplicate_pct,unique_fps\n")
row = (f"{label},{fps_nom},{win:.0f},{total},{uniq},{dup},{dup_pct:.4f},"
       f"{uniq/win:.3f}\n")
newfile = not os.path.exists(out)
with open(out, "a") as fh:
    if newfile:
        fh.write(header)
    fh.write(row)
print(f"[OK] {label}: {uniq}/{total} visually distinct frames "
      f"({dup} duplicates, {dup_pct:.2f}%)  unique_fps={uniq/win:.2f}")
PY

echo "[*] Appended to ${OUT_CSV}"
