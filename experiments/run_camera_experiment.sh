#!/usr/bin/env bash
set -euo pipefail

DURATION=300   # seconds per run (5 min → ~60 STATE samples)
WARMUP=15      # seconds before starting to count

usage() {
    echo "Usage: $0 <num_cameras>"
    echo "  num_cameras: 1, 2, 3, or 4"
    exit 1
}

[[ $# -lt 1 ]] && usage
N="$1"
[[ "$N" =~ ^[1-4]$ ]] || { echo "Error: num_cameras must be 1, 2, 3, or 4"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
SESSIONS_DIR="$ROOT/sessions"

cd "$ROOT"

echo "=================================================="
echo " Camera experiment — N=$N cams — duration=${DURATION}s"
echo "=================================================="

echo "[1/4] Bringing stack up..."
xhost + >/dev/null 2>&1 || true
docker compose up -d --remove-orphans

echo "[2/4] Waiting ${WARMUP}s for services to stabilise..."
sleep "$WARMUP"

# Stop cameras that should not be active
ALL_CAMS=(cam1 cam2 cam3 cam4)
CAMS_TO_STOP=()
for i in "${!ALL_CAMS[@]}"; do
    CAM_NUM=$((i + 1))
    if [[ $CAM_NUM -gt $N ]]; then
        CAMS_TO_STOP+=("${ALL_CAMS[$i]}")
    fi
done

if [[ ${#CAMS_TO_STOP[@]} -gt 0 ]]; then
    echo "[3/4] Stopping unused cameras: ${CAMS_TO_STOP[*]}"
    docker compose stop "${CAMS_TO_STOP[@]}"
else
    echo "[3/4] All 4 cameras active."
fi

# Find the session file that will be written during this run
mkdir -p "$SESSIONS_DIR"
SESSION_BEFORE=$(ls -1 "$SESSIONS_DIR"/session*.jsonl 2>/dev/null | wc -l)
EXPECTED_SESSION=$((SESSION_BEFORE + 1))

echo "[4/4] Collecting telemetry for ${DURATION}s (approx $((DURATION / 5)) STATE samples)..."
echo "      Session file will be: sessions/session${EXPECTED_SESSION}.jsonl"
echo "      Press Ctrl+C to abort early."
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    SAMPLES=$(grep -c '"type": "state"' "$SESSIONS_DIR/session${EXPECTED_SESSION}.jsonl" 2>/dev/null || echo 0)
    printf "  t=%3ds  remaining=%3ds  STATE samples so far: %s\n" "$ELAPSED" "$REMAINING" "$SAMPLES"
done

echo ""
echo "Done. Bringing stack down..."
docker compose down

FINAL_FILE="$SESSIONS_DIR/session${EXPECTED_SESSION}.jsonl"
if [[ -f "$FINAL_FILE" ]]; then
    TOTAL=$(grep -c '"type": "state"' "$FINAL_FILE" || echo 0)
    echo ""
    echo "=================================================="
    echo " Results written to: sessions/session${EXPECTED_SESSION}.jsonl"
    echo " Total STATE samples: $TOTAL"
    echo " Run analysis with:"
    echo "   python3 experiments/analyze_cameras.py sessions/session${EXPECTED_SESSION}.jsonl $N"
    echo "=================================================="
else
    echo "Warning: session file not found at $FINAL_FILE"
fi
