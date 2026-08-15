#!/usr/bin/env bash
# Single source of truth for the video format used in a test cell.
# Regenerates BOTH the voctocore mix config and the docker .env so the
# compositor caps and the camera output can never disagree.
#
# Usage: set_format.sh <1080p25|1080p50|2160p25|2160p50>
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

case "${1:-}" in
  1080p25) W=1920; H=1080; F=25 ;;
  1080p50) W=1920; H=1080; F=50 ;;
  2160p25) W=3840; H=2160; F=25 ;;
  2160p50) W=3840; H=2160; F=50 ;;
  *) echo "Invalid format: '${1:-}'. Use: 1080p25 | 1080p50 | 2160p25 | 2160p50" >&2; exit 1 ;;
esac

CFG="$ROOT/voctocore/default-config.ini"

# Keep one pristine copy of the original config; always regenerate from it
# to avoid cumulative drift across format switches.
[ -f "$CFG.orig" ] || cp "$CFG" "$CFG.orig"

sed -E "s#^videocaps = video/x-raw,format=I420,width=[0-9]+,height=[0-9]+,framerate=[0-9]+/1#videocaps = video/x-raw,format=I420,width=$W,height=$H,framerate=$F/1#" \
    "$CFG.orig" > "$CFG"

# Las previews deben ir al MISMO framerate que el mix: si no, a 50fps GStreamer
# no puede enlazar videoscale->jpegenc (videoscale no convierte framerate) y
# voctocore crashes. The framerate of the previews line (1024x576) is adjusted accordingly.
sed -i -E "s#(videocaps=video/x-raw,width=1024,height=576,framerate=)[0-9]+/1#\1$F/1#" "$CFG"

# Camera output format for docker compose (read as ${WIDTH} etc.).
# SAVE_LOGS=true makes the telemetry service write CPU%/RAM% to
# sessions/sessionN.jsonl (needed for Analysis 1; harmless for the rest).
cat > "$ROOT/.env" <<EOF
WIDTH=$W
HEIGHT=$H
FRAMERATE=$F
AUDIORATE=48000
SAVE_LOGS=true
EOF

echo "Formato aplicado: $1  ($W x $H @ ${F}fps)"
echo "--- voctocore videocaps ---"
grep -E '^videocaps = ' "$CFG"
echo "--- .env (docker cameras) ---"
cat "$ROOT/.env"

# Safety gate: the two must always match.
if ! grep -q "width=$W,height=$H,framerate=$F/1" "$CFG"; then
  echo "ERROR: la config de voctocore no refleja el formato pedido" >&2
  exit 1
fi
