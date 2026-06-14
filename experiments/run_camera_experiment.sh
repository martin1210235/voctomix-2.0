#!/usr/bin/env bash
set -euo pipefail

DURATION=300   # seconds per run (5 min → ~60 STATE samples)
WARMUP=20      # seconds before starting to count (longer: testsrc2 connects fast)

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
echo " Source: testsrc2 (local synthetic, infinite loop)"
echo "=================================================="

echo "[1/5] Bringing stack up with experiment override (SAVE_LOGS=true)..."
xhost + >/dev/null 2>&1 || true
export SAVE_LOGS=true
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    up -d --remove-orphans

echo "[2/5] Waiting ${WARMUP}s for services to stabilise..."
sleep "$WARMUP"

# Verify voctocore is healthy before proceeding
until docker exec voctocore bash -c "echo '' | nc -zw1 localhost 9999" >/dev/null 2>&1; do
    echo "  ... waiting for voctocore port 9999"
    sleep 3
done
echo "  voctocore ready."

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
    echo "[3/5] Stopping unused cameras: ${CAMS_TO_STOP[*]}"
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.experiments.yml \
        stop "${CAMS_TO_STOP[@]}"
    echo "  Waiting 5s for voctocore to detect disconnections..."
    sleep 5
else
    echo "[3/5] All 4 cameras active."
fi

# Find the session file that will be written during this run
mkdir -p "$SESSIONS_DIR"
SESSION_INDEX=1
while [[ -f "$SESSIONS_DIR/session${SESSION_INDEX}.jsonl" ]]; do
    SESSION_INDEX=$((SESSION_INDEX + 1))
done

# Give telemetry a moment to create the file after the stack is fully up
sleep 5
SESSION_FILE="$SESSIONS_DIR/session${SESSION_INDEX}.jsonl"
echo "  Session file: sessions/session${SESSION_INDEX}.jsonl"

# For N=4: launch latency measurement in parallel
LATENCY_PID=""
if [[ "$N" -eq 4 ]]; then
    echo "[4/5] N=4: launching parallel latency measurement (30 switches × 4s)..."
    # Wait for telemetry to write at least one STATE before starting latency
    until grep -q '"type": "state"' "$SESSION_FILE" 2>/dev/null; do sleep 2; done
    python3 "$SCRIPT_DIR/measure_latency.py" "$SESSION_FILE" localhost 9999 &
    LATENCY_PID=$!
    echo "  Latency measurement PID: $LATENCY_PID"
else
    echo "[4/5] Collecting telemetry for ${DURATION}s (approx $((DURATION / 5)) STATE samples)..."
fi

echo "[5/5] Collecting telemetry for ${DURATION}s..."
echo "      Press Ctrl+C to abort early."
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    STATE_N=$(grep -c '"type": "state"' "$SESSION_FILE" 2>/dev/null || echo 0)
    LAT_N=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)
    # Quick cam connectivity check
    CAMS=$(docker ps --format "{{.Names}}" | grep "^cam" | sort | tr '\n' ' ')
    printf "  t=%3ds  rem=%3ds  STATE:%s  latency:%s  cams:[%s]\n" \
        "$ELAPSED" "$REMAINING" "$STATE_N" "$LAT_N" "${CAMS:-none}"
done

# Wait for latency process to finish if still running
if [[ -n "$LATENCY_PID" ]] && kill -0 "$LATENCY_PID" 2>/dev/null; then
    echo ""
    echo "Waiting for latency measurement to complete..."
    wait "$LATENCY_PID" || true
fi

echo ""
echo "Done. Bringing stack down..."
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    down

STATE_TOTAL=$(grep -c '"type": "state"' "$SESSION_FILE" 2>/dev/null || echo 0)
LAT_TOTAL=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)

echo ""
echo "=================================================="
echo " Results: sessions/session${SESSION_INDEX}.jsonl"
echo " STATE samples : $STATE_TOTAL"
echo " Latency events: $LAT_TOTAL"
echo " Run analysis  :"
echo "   python3 experiments/analyze_cameras.py sessions/session${SESSION_INDEX}.jsonl $N"
echo "=================================================="
