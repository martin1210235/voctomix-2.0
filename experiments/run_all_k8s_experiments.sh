#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/k8s_experiment_run.log"
SESSIONS_DIR="$SCRIPT_DIR/../sessions"

echo "Starting all K8s camera experiments — $(date)" | tee "$LOG"
echo "Log: $LOG"
echo ""

declare -A SESSION_MAP

for N in 1 2 3 4; do
    echo "========================================" | tee -a "$LOG"
    echo "  K8s Experiment N=$N — $(date)"         | tee -a "$LOG"
    echo "========================================" | tee -a "$LOG"

    IDX=1
    while [[ -f "$SESSIONS_DIR/session${IDX}.jsonl" ]]; do IDX=$((IDX+1)); done
    SESSION_MAP[$N]=$IDX

    "$SCRIPT_DIR/run_k8s_experiment.sh" "$N" 2>&1 | tee -a "$LOG"
    echo "" | tee -a "$LOG"

    if [[ $N -lt 4 ]]; then
        echo "Cooling down 30s before next experiment..." | tee -a "$LOG"
        sleep 30
    fi
done

echo "" | tee -a "$LOG"
echo "ALL K8s EXPERIMENTS DONE — $(date)" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Run analysis (Docker vs K8s):" | tee -a "$LOG"

# Print the analyze command with correct session numbers
# Assumes Docker sessions are 32-35 (from previous run) — update if needed
for N in 1 2 3 4; do
    IDX="${SESSION_MAP[$N]}"
    echo "  K8s N=$N → sessions/session${IDX}.jsonl" | tee -a "$LOG"
done
