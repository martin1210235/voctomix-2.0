#!/usr/bin/env bash
# run_rapl_repeat.sh — Repeat RAPL energy measurements for both Docker and K8s.
#
# Runs 4 Docker sessions (N=1..4), then 4 K8s sessions (N=1..4), then prints
# a ready-to-paste summary of net RAPL values for RESULTADOS_CAP5.md.
#
# IMPORTANT: Run this ONLY after any K8s resilience or stability tests finish.
# The Docker experiments stop minikube, which kills running K8s pods.
#
# Usage:
#   cd /home/sonda/Documentos/voctomix
#   bash experiments/run_rapl_repeat.sh
#
# Total duration: ~23 min Docker + ~25 min K8s = ~50 min

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
SESSIONS="$ROOT/sessions"
LOG="$SCRIPT_DIR/rapl_repeat_$(date +%Y%m%d_%H%M%S).log"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
separator() { echo "════════════════════════════════════════════════" | tee -a "$LOG"; }

separator
log "RAPL REPEAT EXPERIMENT"
log "Log: $LOG"
separator

# ── Safety check: no K8s resilience test running ──────────────────────────────
if kubectl get pods -l app=studio --field-selector=status.phase=Running \
       -o name 2>/dev/null | grep -q pod; then
    log "WARNING: Main studio pod is running in K8s."
    log "Docker experiments will stop minikube and kill it."
    read -p "Continue anyway? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || { log "Aborted."; exit 1; }
fi

# ── Track session indices before and after each experiment ────────────────────
next_session() {
    local idx=1
    while [[ -f "$SESSIONS/session${idx}.jsonl" ]]; do idx=$((idx + 1)); done
    echo "$idx"
}

declare -A DOCKER_IDX K8S_IDX

# ════════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Docker experiments (N=1..4)
# ════════════════════════════════════════════════════════════════════════════════
separator
log "PHASE 1 — Docker Compose (N=1 to 4)"
separator

for N in 1 2 3 4; do
    DOCKER_IDX[$N]=$(next_session)
    log "Starting Docker N=$N  →  session${DOCKER_IDX[$N]}.jsonl"
    bash "$SCRIPT_DIR/run_camera_experiment.sh" "$N" 2>&1 | tee -a "$LOG"
    if [[ $N -lt 4 ]]; then
        log "Cooling 30s..."
        sleep 30
    fi
done

log "PHASE 1 complete."
separator

# ── Restart minikube for Phase 2 ──────────────────────────────────────────────
log "Restarting minikube for K8s experiments..."
minikube start --driver=docker --cpus=max --memory=max 2>&1 | tail -5 | tee -a "$LOG"
log "Waiting 60s for control plane to stabilize..."
sleep 60

# ── Scale down studio pod (CRITICAL: prevents baseline contamination) ──────────
# When minikube restarts, existing deployments (in 'default' or 'voctomix')
# auto-restore. The studio pod consumes ~25W (RAPL), inflating the K8s idle
# baseline and producing wrong or negative net energy values.
log "Scaling down studio deployments to isolate K8s baseline..."
for NS in default voctomix; do
    if kubectl get deployment studio -n "$NS" 2>/dev/null | grep -q "studio"; then
        log "  Scaling down studio in namespace: $NS"
        kubectl scale deployment studio -n "$NS" --replicas=0 2>/dev/null | tee -a "$LOG" || true
        kubectl wait --for=delete pods -l app=studio -n "$NS" --timeout=120s 2>/dev/null | tee -a "$LOG" || true
    fi
done
log "Waiting 30s for RAPL/CPU to settle after studio pod exit..."
sleep 30

# ════════════════════════════════════════════════════════════════════════════════
# PHASE 2 — K8s experiments (N=1..4)
# ════════════════════════════════════════════════════════════════════════════════
separator
log "PHASE 2 — Kubernetes / minikube (N=1 to 4)"
separator

for N in 1 2 3 4; do
    # Guard: ensure previous voctomix-exp namespace is fully gone before applying the next
    if kubectl get namespace voctomix-exp 2>/dev/null | grep -q "Terminating"; then
        log "Waiting for voctomix-exp namespace to fully terminate before N=$N..."
        kubectl wait --for=delete namespace/voctomix-exp --timeout=120s 2>/dev/null | tee -a "$LOG" || true
        sleep 10
    fi
    K8S_IDX[$N]=$(next_session)
    log "Starting K8s N=$N  →  session${K8S_IDX[$N]}.jsonl"
    bash "$SCRIPT_DIR/run_k8s_experiment.sh" "$N" 2>&1 | tee -a "$LOG"
    if [[ $N -lt 4 ]]; then
        log "Cooling 30s..."
        sleep 30
    fi
done

log "PHASE 2 complete."
separator

# ════════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Extract RAPL results
# ════════════════════════════════════════════════════════════════════════════════
separator
log "PHASE 3 — Extracting RAPL net values"
separator

extract_rapl() {
    local session="$1"
    local baseline="$2"
    python3 - "$session" "$baseline" <<'PYEOF'
import json, sys, statistics, pathlib

session_path = sys.argv[1]
baseline_path = sys.argv[2]

with open(baseline_path) as f:
    b = json.load(f)
baseline_w = b.get("rapl_w") or b.get("rapl_watts") or b.get("watts_rapl", 0)

watts = []
with open(session_path) as f:
    for line in f:
        try:
            ev = json.loads(line)
            if ev.get("type") == "power" and "watts_rapl" in ev:
                watts.append(ev["watts_rapl"])
        except Exception:
            pass

if not watts:
    print("0.0")
else:
    median_w = statistics.median(watts)
    net_w = round(median_w - baseline_w, 1)
    print(f"{net_w}")
PYEOF
}

extract_baseline_rapl() {
    local baseline="$1"
    python3 -c "
import json, sys
with open('$1') as f:
    b = json.load(f)
print(b.get('rapl_w') or b.get('rapl_watts') or b.get('watts_rapl', 0))
"
}

echo "" | tee -a "$LOG"
echo "╔══════════════════════════════════════════╗" | tee -a "$LOG"
echo "║  RAPL NET RESULTS (W) — COPY TO CAP5    ║" | tee -a "$LOG"
echo "╠══════════════════════════════════════════╣" | tee -a "$LOG"
echo "║  N │ Docker baseline │ Docker net │       ║" | tee -a "$LOG"

for N in 1 2 3 4; do
    IDX="${DOCKER_IDX[$N]}"
    BF="$SESSIONS/session${IDX}_baseline.json"
    SF="$SESSIONS/session${IDX}.jsonl"
    BL=$(extract_baseline_rapl "$BF")
    NET=$(extract_rapl "$SF" "$BF")
    printf "║  %d │    %6s W    │  %5s W   │\n" "$N" "$BL" "$NET" | tee -a "$LOG"
done

echo "╠══════════════════════════════════════════╣" | tee -a "$LOG"
echo "║  N │  K8s baseline   │   K8s net  │       ║" | tee -a "$LOG"

for N in 1 2 3 4; do
    IDX="${K8S_IDX[$N]}"
    BF="$SESSIONS/session${IDX}_baseline_k8s.json"
    SF="$SESSIONS/session${IDX}.jsonl"
    BL=$(extract_baseline_rapl "$BF")
    NET=$(extract_rapl "$SF" "$BF")
    printf "║  %d │    %6s W    │  %5s W   │\n" "$N" "$BL" "$NET" | tee -a "$LOG"
done

echo "╚══════════════════════════════════════════╝" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Docker session indices: N1=${DOCKER_IDX[1]} N2=${DOCKER_IDX[2]} N3=${DOCKER_IDX[3]} N4=${DOCKER_IDX[4]}" | tee -a "$LOG"
echo "K8s    session indices: N1=${K8S_IDX[1]} N2=${K8S_IDX[2]} N3=${K8S_IDX[3]} N4=${K8S_IDX[4]}" | tee -a "$LOG"
echo "" | tee -a "$LOG"
log "ALL DONE. Update RESULTADOS_CAP5.md and 5_3_resultados.tex with the values above."
log "Then run Claude to update the LaTeX graph and text."
