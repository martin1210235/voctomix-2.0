#!/usr/bin/env bash
set -euo pipefail

DURATION=300   # seconds per run (5 min → ~60 STATE samples at 5s cadence)
WARMUP=20      # seconds before stopping unused cameras

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
echo " Source: testsrc2 (local synthetic, infinite)"
echo " Energy: RAPL hardware sensor"
echo "=================================================="

# ── [PRE] Stop minikube to avoid CPU/energy contamination ─────────────────────
if docker inspect minikube >/dev/null 2>&1; then
    STATUS=$(docker inspect --format "{{.State.Status}}" minikube 2>/dev/null || echo "unknown")
    if [[ "$STATUS" == "running" ]]; then
        echo "[PRE] Stopping minikube (prevents CPU/energy contamination)..."
        minikube stop 2>/dev/null || docker stop minikube 2>/dev/null || true
        sleep 5
        echo "  minikube stopped."
    fi
fi

# ── [1] Start stack ────────────────────────────────────────────────────────────
echo "[1/6] Bringing stack up with experiment override (SAVE_LOGS=true)..."
xhost + >/dev/null 2>&1 || true
export SAVE_LOGS=true
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    up -d --remove-orphans

# ── [2] Wait for voctocore ────────────────────────────────────────────────────
echo "[2/6] Waiting ${WARMUP}s and verifying voctocore readiness..."
sleep "$WARMUP"
until docker exec voctocore bash -c "echo '' | nc -zw1 localhost 9999" >/dev/null 2>&1; do
    echo "  ... waiting for voctocore port 9999"
    sleep 3
done
echo "  voctocore ready."

# ── [3] Stop unused cameras ───────────────────────────────────────────────────
ALL_CAMS=(cam1 cam2 cam3 cam4)
CAMS_TO_STOP=()
for i in "${!ALL_CAMS[@]}"; do
    if [[ $((i + 1)) -gt $N ]]; then
        CAMS_TO_STOP+=("${ALL_CAMS[$i]}")
    fi
done

if [[ ${#CAMS_TO_STOP[@]} -gt 0 ]]; then
    echo "[3/6] Stopping unused cameras: ${CAMS_TO_STOP[*]}"
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.experiments.yml \
        stop "${CAMS_TO_STOP[@]}"
    echo "  Waiting 5s for voctocore to detect disconnections..."
    sleep 5
else
    echo "[3/6] All 4 cameras active."
fi

# ── [4] Locate session file ───────────────────────────────────────────────────
mkdir -p "$SESSIONS_DIR"
SESSION_INDEX=1
while [[ -f "$SESSIONS_DIR/session${SESSION_INDEX}.jsonl" ]]; do
    SESSION_INDEX=$((SESSION_INDEX + 1))
done
sleep 5   # give telemetry time to create the file
SESSION_FILE="$SESSIONS_DIR/session${SESSION_INDEX}.jsonl"
echo "[4/6] Session file: sessions/session${SESSION_INDEX}.jsonl"

# ── [5] Start parallel background measurements ────────────────────────────────
echo "[5/6] Starting background measurements..."

# RAPL energy scraper (always — runs on host, no Docker needed)
until [[ -f "$SESSION_FILE" ]]; do sleep 1; done
python3 "$SCRIPT_DIR/rapl_scraper.py" "$SESSION_FILE" 5 &
RAPL_PID=$!
echo "  RAPL scraper PID: $RAPL_PID"

# Latency measurement (only N=4 — needs multiple sources available)
LATENCY_PID=""
if [[ "$N" -eq 4 ]]; then
    until grep -q '"type": "state"' "$SESSION_FILE" 2>/dev/null; do sleep 2; done
    python3 "$SCRIPT_DIR/measure_latency.py" "$SESSION_FILE" localhost 9999 &
    LATENCY_PID=$!
    echo "  Latency measurement PID: $LATENCY_PID"
fi

# ── [6] Collect telemetry ─────────────────────────────────────────────────────
echo "[6/6] Collecting ${DURATION}s of telemetry..."
echo "      Press Ctrl+C to abort early."
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    STATE_N=$(grep -c '"type": "state"'   "$SESSION_FILE" 2>/dev/null || echo 0)
    POWER_N=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
    LAT_N=$(grep -c   '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)
    CAMS=$(docker ps --format "{{.Names}}" | grep "^cam" | sort | tr '\n' ' ')
    printf "  t=%3ds rem=%3ds | STATE:%-3s POWER:%-3s LAT:%-3s | cams:[%s]\n" \
        "$ELAPSED" "$REMAINING" "$STATE_N" "$POWER_N" "$LAT_N" "${CAMS:-none}"
done

# Wait for background processes
if [[ -n "$LATENCY_PID" ]] && kill -0 "$LATENCY_PID" 2>/dev/null; then
    echo "Waiting for latency measurement to complete..."
    wait "$LATENCY_PID" || true
fi
kill "$RAPL_PID" 2>/dev/null || true

# ── Bring stack down ──────────────────────────────────────────────────────────
echo ""
echo "Bringing stack down..."
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    down

# ── Summary ───────────────────────────────────────────────────────────────────
STATE_TOTAL=$(grep -c '"type": "state"'   "$SESSION_FILE" 2>/dev/null || echo 0)
POWER_TOTAL=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
LAT_TOTAL=$(grep -c   '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)

echo ""
echo "=================================================="
echo " Results: sessions/session${SESSION_INDEX}.jsonl"
echo " STATE samples  : $STATE_TOTAL"
echo " POWER (RAPL)   : $POWER_TOTAL"
echo " Latency events : $LAT_TOTAL"
echo " Analyse with   :"
echo "   python3 experiments/analyze_cameras.py sessions/session${SESSION_INDEX}.jsonl $N"
echo "=================================================="
