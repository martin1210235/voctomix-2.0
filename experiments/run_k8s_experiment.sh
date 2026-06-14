#!/usr/bin/env bash
set -euo pipefail

DURATION=300
WARMUP=35
BASELINE_SECS=30
NS=voctomix-exp
MANIFESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../k8s_escenario/experiments" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
SESSIONS_DIR="$ROOT/sessions"
mkdir -p "$SESSIONS_DIR"

usage() { echo "Usage: $0 <num_cameras>  (1-4)"; exit 1; }
[[ $# -lt 1 ]] && usage
N="$1"
[[ "$N" =~ ^[1-4]$ ]] || { echo "num_cameras must be 1-4"; exit 1; }

echo "=================================================="
echo " K8s experiment — N=$N cams — duration=${DURATION}s"
echo " Cluster: minikube (driver: docker)"
echo " Energy:  RAPL hardware sensor"
echo "=================================================="

# ── [PRE] Ensure minikube is running ──────────────────────────────────────────
if ! minikube status 2>/dev/null | grep -q "Running"; then
    echo "[PRE] Starting minikube..."
    minikube start --driver=docker --cpus=max --memory=max 2>&1 | tail -5
else
    echo "[PRE] minikube already running."
fi

# ── [1] Determine session index ───────────────────────────────────────────────
SESSION_INDEX=1
while [[ -f "$SESSIONS_DIR/session${SESSION_INDEX}.jsonl" ]]; do
    SESSION_INDEX=$((SESSION_INDEX + 1))
done
SESSION_FILE="$SESSIONS_DIR/session${SESSION_INDEX}.jsonl"
BASELINE_FILE="$SESSIONS_DIR/session${SESSION_INDEX}_baseline_k8s.json"
echo "[1/8] Session will be: sessions/session${SESSION_INDEX}.jsonl"

# ── [2] Measure baseline BEFORE image load (clean K8s-idle state) ─────────────
echo "[2/8] Measuring ${BASELINE_SECS}s baseline (minikube running, no voctomix)..."
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
    return vals[3], sum(vals)

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

cpu_pct = round(100.0 * (1.0 - (idle1 - idle0) / (tot1 - tot0)), 1)
rapl_w  = round(delta_uj / (t1 - t0) / 1e6, 2)
ram_pct = read_mem()

baseline = {
    "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "scenario":   "kubernetes",
    "duration_s": secs,
    "cpu_pct":    cpu_pct,
    "ram_pct":    ram_pct,
    "rapl_watts": rapl_w,
}
with open(out_path, "w") as f:
    json.dump(baseline, f, indent=2)
print(f"  Baseline → CPU: {cpu_pct}%  RAM: {ram_pct}%  RAPL: {rapl_w} W")
PYEOF

# ── [PRE-2] Load image only if not already in minikube ────────────────────────
if ! minikube image ls 2>/dev/null | grep -q "voctomix-voctocore:latest"; then
    echo "[PRE] Loading voctomix image into minikube (first time only)..."
    minikube image load voctomix-voctocore:latest
else
    echo "[PRE] voctomix image already in minikube, skipping load."
fi

# ── [3] Deploy K8s stack ──────────────────────────────────────────────────────
echo "[3/8] Deploying K8s stack in namespace $NS..."
kubectl apply -f "$MANIFESTS_DIR/namespace.yaml"
kubectl apply -f "$MANIFESTS_DIR/rabbitmq.yaml"
kubectl apply -f "$MANIFESTS_DIR/voctocore.yaml"
kubectl apply -f "$MANIFESTS_DIR/telemetry.yaml"
kubectl apply -f "$MANIFESTS_DIR/cameras.yaml"

# ── [4] Wait for readiness ────────────────────────────────────────────────────
echo "[4/8] Waiting for rabbitmq readiness (up to 180s)..."
kubectl wait deployment/rabbitmq -n $NS \
    --for=condition=available --timeout=180s

echo "  Waiting for voctocore readiness (up to 180s)..."
kubectl wait deployment/voctocore -n $NS \
    --for=condition=available --timeout=180s

echo "[4/8] Waiting additional ${WARMUP}s for cameras to connect to voctocore..."
sleep "$WARMUP"

until kubectl exec -n $NS deploy/voctocore -- \
    bash -c "echo '' | nc -zw1 localhost 9999" >/dev/null 2>&1; do
    echo "  ... waiting for voctocore:9999"
    sleep 3
done
echo "  voctocore ready."

# ── [5] Scale down unused cameras ─────────────────────────────────────────────
ALL_CAMS=(cam1 cam2 cam3 cam4)
CAMS_TO_STOP=()
for i in "${!ALL_CAMS[@]}"; do
    if [[ $((i + 1)) -gt $N ]]; then
        CAMS_TO_STOP+=("${ALL_CAMS[$i]}")
    fi
done

if [[ ${#CAMS_TO_STOP[@]} -gt 0 ]]; then
    echo "[5/8] Scaling down unused cameras: ${CAMS_TO_STOP[*]}"
    for CAM in "${CAMS_TO_STOP[@]}"; do
        kubectl scale deployment "$CAM" -n $NS --replicas=0
    done
    # K8s default graceful termination = 30s; wait enough time for voctocore to detect
    echo "  Waiting 40s for K8s pod termination and voctocore to detect disconnection..."
    sleep 40
else
    echo "[5/8] All 4 cameras active."
fi
echo "  Active cameras: ${ALL_CAMS[*]:0:$N}"

# ── [6] Background measurements ───────────────────────────────────────────────
echo "[6/8] Starting background measurements..."

# RAPL scraper on host (writes power entries to SESSION_FILE)
python3 "$SCRIPT_DIR/rapl_scraper.py" "$SESSION_FILE" 5 &
RAPL_PID=$!
echo "  RAPL scraper PID: $RAPL_PID"

# Latency measurement (N=4 only) — needs port-forward to reach K8s voctocore
LATENCY_PID=""
PF_PID=""
if [[ "$N" -eq 4 ]]; then
    echo "  Starting port-forward for voctocore:9999..."
    kubectl port-forward -n $NS deploy/voctocore 9999:9999 >/dev/null 2>&1 &
    PF_PID=$!
    sleep 5  # wait for port-forward to be ready
    until grep -q '"type": "power"' "$SESSION_FILE" 2>/dev/null; do sleep 2; done
    python3 "$SCRIPT_DIR/measure_latency.py" "$SESSION_FILE" localhost 9999 &
    LATENCY_PID=$!
    echo "  Latency measurement PID: $LATENCY_PID  port-forward PID: $PF_PID"
fi

# ── [7] Collect ───────────────────────────────────────────────────────────────
echo "[7/8] Collecting ${DURATION}s of telemetry..."
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    CAMS=$(kubectl get pods -n $NS \
        --no-headers 2>/dev/null \
        | grep -E "^cam[0-9]" | grep "Running" | awk '{print $1}' | tr '\n' ' ')
    P=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
    L=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)
    printf "  t=%3ds rem=%3ds | POWER:%-3s LAT:%-3s | cams:[%s]\n" \
        "$ELAPSED" "$REMAINING" "$P" "$L" "${CAMS:-none}"
done

# Wait for latency to finish
if [[ -n "$LATENCY_PID" ]] && kill -0 "$LATENCY_PID" 2>/dev/null; then
    echo "Waiting for latency measurement to finish..."
    # Kill after 10s if still running (fixed the drain-loop bug)
    wait "$LATENCY_PID" 2>/dev/null || true
fi
[[ -n "$PF_PID" ]] && kill "$PF_PID" 2>/dev/null || true
kill "$RAPL_PID" 2>/dev/null || true

# ── [8] Copy session from telemetry pod and tear down ─────────────────────────
echo ""
echo "[8/8] Copying STATE events from telemetry pod..."
TELEMETRY_POD=$(kubectl get pods -n $NS -l app=telemetry \
    --no-headers -o custom-columns=NAME:.metadata.name 2>/dev/null | head -1)

if [[ -n "$TELEMETRY_POD" ]]; then
    POD_SESSION=$(kubectl exec -n $NS "$TELEMETRY_POD" -- \
        ls /opt/voctomix/sessions/ 2>/dev/null \
        | grep "^session.*\.jsonl" | sort -V | tail -1)
    if [[ -n "$POD_SESSION" ]]; then
        TMP_FILE=$(mktemp)
        kubectl cp "$NS/$TELEMETRY_POD:/opt/voctomix/sessions/$POD_SESSION" "$TMP_FILE"
        cat "$TMP_FILE" >> "$SESSION_FILE"
        rm -f "$TMP_FILE"
        echo "  Merged pod session ($POD_SESSION) into session${SESSION_INDEX}.jsonl"
    else
        echo "  Warning: no session file found inside telemetry pod."
    fi
else
    echo "  Warning: telemetry pod not found."
fi

echo "Tearing down K8s namespace..."
kubectl delete namespace $NS --timeout=90s || true

S_TOT=$(grep -c '"type": "state"'   "$SESSION_FILE" 2>/dev/null || echo 0)
P_TOT=$(grep -c '"type": "power"'   "$SESSION_FILE" 2>/dev/null || echo 0)
L_TOT=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)

echo ""
echo "=================================================="
echo " Results: sessions/session${SESSION_INDEX}.jsonl"
echo " Baseline:      $BASELINE_FILE"
echo " STATE:         $S_TOT"
echo " POWER (RAPL):  $P_TOT"
echo " Latency:       $L_TOT"
echo " Analyse:"
echo "   python3 experiments/analyze_cameras.py \\"
echo "     sessions/session${SESSION_INDEX}.jsonl $N \\"
echo "     sessions/session${SESSION_INDEX}_baseline_k8s.json"
echo "=================================================="
