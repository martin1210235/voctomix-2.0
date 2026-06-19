#!/usr/bin/env bash
# Runs the K8s stability test and generates figuras/estabilidad_30min_k8s.png.
#
# What it does:
#   1. Patches configmap: SAVE_LOGS=true
#   2. Patches deployment: cam1-4 use lavfi (infinite, local) sources
#   3. Fixes deployment image names (pre-existing bug: ${VOCTOMIX_IMAGE} not expanded)
#   4. Rolls out the pod (new pod picks up all three changes)
#   5. Waits for all 10 containers to be Ready
#   6. Waits 35 minutes while telemetry records session data
#   7. Copies the JSONL session file out of the pod
#   8. Generates the stability figure
#   9. Restores configmap (SAVE_LOGS=false) and deployment (HTTP sources)
#  10. Rolls out again to restore original state
#
# Total runtime: ~50 minutes.
# Run from the repo root: bash k8s_escenario/run_k8s_stability.sh

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
K8S_DIR="$BASE_DIR/k8s_escenario"
SESSIONS_DIR="$BASE_DIR/sessions"
TOOLS_DIR="$BASE_DIR/tools"
OUTPUT_FIGURE="$BASE_DIR/memoria_tfg/figuras/estabilidad_30min_k8s.png"
SESSION_LOCAL="$SESSIONS_DIR/session1_k8s.jsonl"
STABILITY_MINUTES=35

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }

wait_for_new_pod() {
    local old_pod="$1"
    local attempts=120
    log "Waiting for new studio pod to appear and all 10 containers to be Ready..."
    while (( attempts > 0 )); do
        local pod
        pod=$(kubectl get pods -l app=studio --field-selector=status.phase=Running \
            -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
        if [[ -n "$pod" && "$pod" != "$old_pod" ]]; then
            local not_ready
            not_ready=$(kubectl get pod "$pod" \
                -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null \
                | tr ' ' '\n' | grep -c "^false$" || true)
            local total
            total=$(kubectl get pod "$pod" \
                -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null \
                | tr ' ' '\n' | grep -c "^" || true)
            if [[ "$total" -eq 10 && "$not_ready" -eq 0 ]]; then
                log "New pod $pod is fully Ready (10/10)."
                echo "$pod"
                return 0
            fi
            log "  $pod: $((total - not_ready))/$total containers ready..."
        elif [[ -n "$pod" && "$pod" == "$old_pod" ]]; then
            log "  Old pod still Running, new pod not yet visible..."
        else
            log "  Waiting for new pod to appear..."
        fi
        sleep 5
        (( attempts-- ))
    done
    log "ERROR: new studio pod did not reach Ready state in 10 minutes."
    exit 1
}

get_latest_session() {
    local pod="$1"
    kubectl exec "$pod" -c telemetry -- \
        sh -c 'ls /opt/voctomix/sessions/session*.jsonl 2>/dev/null | sort -V | tail -1' 2>/dev/null || true
}

echo "============================================================"
echo "  Voctomix K8s Stability Test"
echo "  Duration: ${STABILITY_MINUTES} minutes + ~15 min setup/teardown"
echo "============================================================"

OLD_POD=$(kubectl get pods -l app=studio --field-selector=status.phase=Running \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
log "Current running pod: ${OLD_POD:-none}"

log "Step 1/10 — Patching configmap: SAVE_LOGS=true"
kubectl patch configmap voctomix-config \
    --type merge \
    --patch-file "$K8S_DIR/stability_cm_patch.json"

log "Step 2/10 — Patching deployment: cam1-4 → lavfi sources"
kubectl patch deployment studio \
    --type strategic \
    --patch-file "$K8S_DIR/stability_deploy_patch.json"

log "Step 3/10 — Fixing deployment image names (replacing unexpanded shell vars)"
kubectl patch deployment studio \
    --type strategic \
    --patch-file "$K8S_DIR/fix_images_patch.json"

log "Step 4/10 — Rolling restart..."
kubectl rollout restart deployment/studio
sleep 5

log "Step 5/10 — Waiting for NEW pod ready (old pod: ${OLD_POD:-none})..."
POD=$(wait_for_new_pod "$OLD_POD")

log "Step 6/10 — Recording session for ${STABILITY_MINUTES} minutes..."
log "  Telemetry writing to /opt/voctomix/sessions/ inside pod $POD"
log "  Monitor: kubectl logs -f pod/$POD -c telemetry --since=0s"
echo ""
for min in $(seq 1 "$STABILITY_MINUTES"); do
    sleep 60
    log "  ${min}/${STABILITY_MINUTES} min elapsed..."
done
echo ""

log "Step 7/10 — Locating session file in pod..."
SESSION_POD=$(get_latest_session "$POD")
if [[ -z "$SESSION_POD" ]]; then
    log "ERROR: No session file found in /opt/voctomix/sessions/. Was SAVE_LOGS=true picked up?"
    log "  Check: kubectl exec $POD -c telemetry -- env | grep SAVE_LOGS"
    exit 1
fi
log "  Found: $SESSION_POD"

log "Step 8/10 — Copying session file locally → $SESSION_LOCAL"
mkdir -p "$SESSIONS_DIR"
kubectl cp "$POD:/opt/voctomix/sessions/$(basename "$SESSION_POD")" \
    "$SESSION_LOCAL" -c telemetry
log "  Copied $(wc -l < "$SESSION_LOCAL") lines."

log "Step 9/10 — Generating stability figure..."
python3 "$TOOLS_DIR/analyze_stability.py" \
    "$SESSION_LOCAL" \
    --output "$OUTPUT_FIGURE" \
    --max-minutes 31 \
    --label "Kubernetes (Minikube)"
log "  Figure saved: $OUTPUT_FIGURE"

log "Step 10/10 — Restoring original deployment..."
OLD_POD="$POD"
kubectl patch configmap voctomix-config \
    --type merge \
    --patch-file "$K8S_DIR/restore_cm_patch.json"
kubectl patch deployment studio \
    --type strategic \
    --patch-file "$K8S_DIR/restore_deploy_patch.json"
kubectl rollout restart deployment/studio

echo ""
echo "============================================================"
echo "  Stability test COMPLETE."
echo "  Figure: $OUTPUT_FIGURE"
echo "  Session: $SESSION_LOCAL"
echo ""
echo "  NOTE: Pod is rolling back to HTTP sources (~3 min)."
echo "  For RESILIENCE test: wait 12 min after pod ready, then:"
echo "  python3 tools/measure_resilience_k8s.py"
echo "============================================================"
