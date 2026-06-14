#!/usr/bin/env bash
set -euo pipefail

DURATION=300      # seconds of data collection per run (→ ~60 STATE samples at 5s)
WARMUP=20         # seconds to wait after docker up before stopping unused cameras
BASELINE_SECS=30  # seconds to sample baseline (before docker up)

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
mkdir -p "$SESSIONS_DIR"

cd "$ROOT"

echo "=================================================="
echo " Camera experiment — N=$N cams — duration=${DURATION}s"
echo " Source: testsrc2 (local synthetic, infinite)"
echo " Energy: RAPL hardware sensor"
echo "=================================================="

# ── [PRE] Stop minikube ────────────────────────────────────────────────────────
if docker inspect minikube >/dev/null 2>&1; then
    STATUS=$(docker inspect --format "{{.State.Status}}" minikube 2>/dev/null || echo "unknown")
    if [[ "$STATUS" == "running" ]]; then
        echo "[PRE] Stopping minikube (prevents CPU/energy contamination)..."
        minikube stop 2>/dev/null || docker stop minikube 2>/dev/null || true
        sleep 5
        echo "  minikube stopped."
    fi
fi

# ── [1] Determine session index BEFORE docker up ──────────────────────────────
# Critical: must be done here so rapl_scraper and telemetry agree on filename.
SESSION_INDEX=1
while [[ -f "$SESSIONS_DIR/session${SESSION_INDEX}.jsonl" ]]; do
    SESSION_INDEX=$((SESSION_INDEX + 1))
done
SESSION_FILE="$SESSIONS_DIR/session${SESSION_INDEX}.jsonl"
BASELINE_FILE="$SESSIONS_DIR/session${SESSION_INDEX}_baseline.json"
echo "[1/7] Session will be: sessions/session${SESSION_INDEX}.jsonl"

# ── [2] Measure baseline (docker DOWN, voctomix not running) ──────────────────
echo "[2/7] Measuring ${BASELINE_SECS}s baseline (no voctomix)..."
python3 - "$BASELINE_FILE" "$BASELINE_SECS" <<'PYEOF'
import sys, time, json, pathlib
from datetime import datetime

out_path = sys.argv[1]
secs     = int(sys.argv[2])
RAPL     = pathlib.Path("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj")
MAX_R    = pathlib.Path("/sys/class/powercap/intel-rapl/intel-rapl:0/max_energy_range_uj")

def read_cpu():
    parts = open("/proc/stat").readline().split()[1:]
    vals  = [float(x) for x in parts]
    return vals[3], sum(vals)   # idle, total

def read_mem():
    m = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":")
        m[k.strip()] = int(v.split()[0])
    return round(100.0 * (m["MemTotal"] - m["MemAvailable"]) / m["MemTotal"], 1)

idle0, tot0 = read_cpu()
e0 = int(RAPL.read_text())
t0 = time.monotonic()
time.sleep(secs)
idle1, tot1 = read_cpu()
e1 = int(RAPL.read_text())
t1 = time.monotonic()

max_range = int(MAX_R.read_text())
delta_uj  = e1 - e0
if delta_uj < 0:
    delta_uj += max_range

cpu_pct   = round(100.0 * (1.0 - (idle1 - idle0) / (tot1 - tot0)), 1)
rapl_w    = round(delta_uj / (t1 - t0) / 1e6, 2)
ram_pct   = read_mem()

baseline = {
    "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "duration_s":   secs,
    "cpu_pct":      cpu_pct,
    "ram_pct":      ram_pct,
    "rapl_watts":   rapl_w,
}
with open(out_path, "w") as f:
    json.dump(baseline, f, indent=2)

print(f"  Baseline → CPU: {cpu_pct}%  RAM: {ram_pct}%  RAPL: {rapl_w} W")
PYEOF

# ── [3] Start stack ────────────────────────────────────────────────────────────
echo "[3/7] Bringing stack up (SAVE_LOGS=true)..."
xhost + >/dev/null 2>&1 || true
export SAVE_LOGS=true
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    up -d --remove-orphans

# ── [4] Wait for voctocore ─────────────────────────────────────────────────────
echo "[4/7] Waiting ${WARMUP}s then verifying voctocore..."
sleep "$WARMUP"
until docker exec voctocore bash -c "echo '' | nc -zw1 localhost 9999" >/dev/null 2>&1; do
    echo "  ... waiting for voctocore:9999"
    sleep 3
done
echo "  voctocore ready."

# ── [5] Stop unused cameras ────────────────────────────────────────────────────
ALL_CAMS=(cam1 cam2 cam3 cam4)
CAMS_TO_STOP=()
for i in "${!ALL_CAMS[@]}"; do
    [[ $((i + 1)) -gt $N ]] && CAMS_TO_STOP+=("${ALL_CAMS[$i]}")
done

if [[ ${#CAMS_TO_STOP[@]} -gt 0 ]]; then
    echo "[5/7] Stopping unused cameras: ${CAMS_TO_STOP[*]}"
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.experiments.yml \
        stop "${CAMS_TO_STOP[@]}"
    echo "  Waiting 8s for voctocore to detect disconnections..."
    sleep 8
else
    echo "[5/7] All 4 cameras active."
fi

# ── [6] Start background measurements ─────────────────────────────────────────
echo "[6/7] Starting background measurements..."

# Wait for telemetry to create the session file
until [[ -f "$SESSION_FILE" ]]; do sleep 1; done
echo "  Session file confirmed: $SESSION_FILE"

# RAPL scraper (always, on host)
python3 "$SCRIPT_DIR/rapl_scraper.py" "$SESSION_FILE" 5 &
RAPL_PID=$!
echo "  RAPL scraper PID: $RAPL_PID"

# Latency measurement (N=4 only — needs 4 sources to cycle through)
LATENCY_PID=""
if [[ "$N" -eq 4 ]]; then
    until grep -q '"type": "state"' "$SESSION_FILE" 2>/dev/null; do sleep 2; done
    python3 "$SCRIPT_DIR/measure_latency.py" "$SESSION_FILE" localhost 9999 &
    LATENCY_PID=$!
    echo "  Latency measurement PID: $LATENCY_PID"
fi

# ── [7] Collect ────────────────────────────────────────────────────────────────
echo "[7/7] Collecting ${DURATION}s of telemetry..."
echo "      (Progress every 10s — Ctrl+C to abort)"
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    S=$(grep -c '"type": "state"'   "$SESSION_FILE" 2>/dev/null || echo 0)
    P=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
    L=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)
    CAMS=$(docker ps --format "{{.Names}}" | grep "^cam" | sort | tr '\n' ' ')
    printf "  t=%3ds rem=%3ds | STATE:%-3s POWER:%-3s LAT:%-3s | cams:[%s]\n" \
        "$ELAPSED" "$REMAINING" "$S" "$P" "$L" "${CAMS:-none}"
done

# Wait for latency to finish
if [[ -n "$LATENCY_PID" ]] && kill -0 "$LATENCY_PID" 2>/dev/null; then
    echo "Waiting for latency measurement to finish..."
    wait "$LATENCY_PID" || true
fi
kill "$RAPL_PID" 2>/dev/null || true

# ── Tear down ──────────────────────────────────────────────────────────────────
echo ""
echo "Bringing stack down..."
docker compose \
    -f docker-compose.yml \
    -f docker-compose.experiments.yml \
    down

# ── Summary ────────────────────────────────────────────────────────────────────
S_TOT=$(grep -c '"type": "state"'   "$SESSION_FILE" 2>/dev/null || echo 0)
P_TOT=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
L_TOT=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)

echo ""
echo "=================================================="
echo " Results: sessions/session${SESSION_INDEX}.jsonl"
echo " Baseline:      $BASELINE_FILE"
echo " STATE:         $S_TOT samples"
echo " POWER (RAPL):  $P_TOT samples"
echo " Latency:       $L_TOT samples"
echo ""
echo " Analyse with:"
echo "   python3 experiments/analyze_cameras.py \\"
echo "     sessions/session${SESSION_INDEX}.jsonl $N \\"
echo "     sessions/session${SESSION_INDEX}_baseline.json"
echo "=================================================="
