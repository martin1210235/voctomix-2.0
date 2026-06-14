#!/usr/bin/env bash
set -euo pipefail

DURATION=300
WARMUP=30
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

# ── [PRE] Load voctomix image into minikube ───────────────────────────────────
echo "[PRE] Loading voctomix image into minikube..."
minikube image load voctomix-voctocore:latest 2>&1 | tail -3

# ── [1] Determine session index BEFORE deploying ──────────────────────────────
SESSION_INDEX=1
while [[ -f "$SESSIONS_DIR/session${SESSION_INDEX}.jsonl" ]]; do
    SESSION_INDEX=$((SESSION_INDEX + 1))
done
SESSION_FILE="$SESSIONS_DIR/session${SESSION_INDEX}.jsonl"
BASELINE_FILE="$SESSIONS_DIR/session${SESSION_INDEX}_baseline_k8s.json"
echo "[1/8] Session will be: sessions/session${SESSION_INDEX}.jsonl"

# ── [2] Measure baseline ──────────────────────────────────────────────────────
echo "[2/8] Measuring ${BASELINE_SECS}s baseline (K8s idle, no voctomix pods)..."
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

cpu_pct   = round(100.0 * (1.0 - (idle1 - idle0) / (tot1 - tot0)), 1)
rapl_w    = round(delta_uj / (t1 - t0) / 1e6, 2)
ram_pct   = read_mem()

baseline = {
    "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "scenario":     "kubernetes",
    "duration_s":   secs,
    "cpu_pct":      cpu_pct,
    "ram_pct":      ram_pct,
    "rapl_watts":   rapl_w,
}
with open(out_path, "w") as f:
    json.dump(baseline, f, indent=2)
print(f"  Baseline → CPU: {cpu_pct}%  RAM: {ram_pct}%  RAPL: {rapl_w} W")
PYEOF

# ── [3] Deploy K8s stack ──────────────────────────────────────────────────────
echo "[3/8] Deploying K8s stack in namespace $NS..."
kubectl apply -f "$MANIFESTS_DIR/namespace.yaml"
kubectl apply -f "$MANIFESTS_DIR/rabbitmq.yaml"
kubectl apply -f "$MANIFESTS_DIR/voctocore.yaml"
kubectl apply -f "$MANIFESTS_DIR/telemetry.yaml"
kubectl apply -f "$MANIFESTS_DIR/cameras.yaml"

# ── [4] Wait for readiness ────────────────────────────────────────────────────
echo "[4/8] Waiting for rabbitmq readiness..."
kubectl wait deployment/rabbitmq -n $NS \
    --for=condition=available --timeout=120s

echo "  Waiting for voctocore readiness..."
kubectl wait deployment/voctocore -n $NS \
    --for=condition=available --timeout=120s

echo "[4/8] Waiting additional ${WARMUP}s for pipeline stabilisation..."
sleep "$WARMUP"

# Verify voctocore port is responding
until kubectl exec -n $NS deploy/voctocore -- \
    bash -c "echo '' | nc -zw1 localhost 9999" >/dev/null 2>&1; do
    echo "  ... waiting for voctocore:9999"
    sleep 3
done
echo "  voctocore ready."

# ── [5] Scale down unused cameras ─────────────────────────────────────────────
ALL_CAMS=(cam1 cam2 cam3 cam4)
for i in "${!ALL_CAMS[@]}"; do
    if [[ $((i + 1)) -gt $N ]]; then
        echo "[5/8] Scaling down ${ALL_CAMS[$i]}..."
        kubectl scale deployment "${ALL_CAMS[$i]}" -n $NS --replicas=0
    fi
done
[[ $N -lt 4 ]] && { echo "  Waiting 8s for voctocore to detect disconnections..."; sleep 8; }
echo "  Active cameras: ${ALL_CAMS[@]:0:$N}"

# ── [6] Find session file in pod and start background measurements ─────────────
echo "[6/8] Starting background measurements..."

# RAPL scraper on host
python3 "$SCRIPT_DIR/rapl_scraper.py" "$SESSION_FILE" 5 &
RAPL_PID=$!
echo "  RAPL scraper PID: $RAPL_PID (writing to temp path, will merge)"

# Latency measurement at N=4
LATENCY_PID=""
if [[ "$N" -eq 4 ]]; then
    sleep 15  # give telemetry time to start
    python3 "$SCRIPT_DIR/measure_latency.py" "$SESSION_FILE" localhost 9999 &
    LATENCY_PID=$!
    echo "  Latency measurement PID: $LATENCY_PID"
fi

# ── [7] Collect ───────────────────────────────────────────────────────────────
echo "[7/8] Collecting ${DURATION}s of telemetry..."
echo "      (K8s telemetry is inside the pod — session file copied at the end)"
echo ""

ELAPSED=0
INTERVAL=10
while [[ $ELAPSED -lt $DURATION ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    REMAINING=$((DURATION - ELAPSED))
    CAMS=$(kubectl get pods -n $NS -l 'app in (cam1,cam2,cam3,cam4)' \
        --field-selector=status.phase=Running \
        --no-headers 2>/dev/null | awk '{print $1}' | tr '\n' ' ')
    P=$(grep -c '"type": "power"' "$SESSION_FILE" 2>/dev/null || echo 0)
    L=$(grep -c '"type": "latency"' "$SESSION_FILE" 2>/dev/null || echo 0)
    printf "  t=%3ds rem=%3ds | POWER:%-3s LAT:%-3s | pods:[%s]\n" \
        "$ELAPSED" "$REMAINING" "$P" "$L" "${CAMS:-none}"
done

# Wait for latency to finish
if [[ -n "$LATENCY_PID" ]] && kill -0 "$LATENCY_PID" 2>/dev/null; then
    echo "Waiting for latency measurement..."
    wait "$LATENCY_PID" || true
fi
kill "$RAPL_PID" 2>/dev/null || true

# ── [8] Copy session file from pod and tear down ──────────────────────────────
echo ""
echo "[8/8] Copying session file from telemetry pod..."
TELEMETRY_POD=$(kubectl get pods -n $NS -l app=telemetry \
    --no-headers -o custom-columns=NAME:.metadata.name 2>/dev/null | head -1)

if [[ -n "$TELEMETRY_POD" ]]; then
    # Find the session file inside the pod (session index starts at 1 inside fresh pod)
    POD_SESSION=$(kubectl exec -n $NS "$TELEMETRY_POD" -- \
        ls /opt/voctomix/sessions/ 2>/dev/null | grep "^session.*\.jsonl" | tail -1)
    if [[ -n "$POD_SESSION" ]]; then
        kubectl cp "$NS/$TELEMETRY_POD:/opt/voctomix/sessions/$POD_SESSION" \
            "$SESSION_FILE.state_events"
        echo "  Copied pod session: $POD_SESSION → session${SESSION_INDEX}.jsonl.state_events"
        # Merge state events into main session file (which has RAPL and latency)
        cat "$SESSION_FILE.state_events" >> "$SESSION_FILE" || true
        rm -f "$SESSION_FILE.state_events"
    else
        echo "  Warning: no session file found in pod."
    fi
else
    echo "  Warning: telemetry pod not found."
fi

echo "Tearing down K8s stack..."
kubectl delete namespace $NS --timeout=60s || true

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
echo " Analyse with:"
echo "   python3 experiments/analyze_cameras.py \\"
echo "     sessions/session${SESSION_INDEX}.jsonl $N \\"
echo "     sessions/session${SESSION_INDEX}_baseline_k8s.json"
echo "=================================================="
