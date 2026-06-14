#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/experiment_run.log"
SESSIONS_DIR="$SCRIPT_DIR/../sessions"

echo "Starting all camera experiments — $(date)" | tee "$LOG"
echo "Log: $LOG"
echo ""

# Track which session files are created
declare -A SESSION_MAP   # N → session index

for N in 1 2 3 4; do
    echo "========================================" | tee -a "$LOG"
    echo "  Experiment N=$N — $(date)"             | tee -a "$LOG"
    echo "========================================" | tee -a "$LOG"

    # Record next available session index before this run
    IDX=1
    while [[ -f "$SESSIONS_DIR/session${IDX}.jsonl" ]]; do IDX=$((IDX+1)); done
    SESSION_MAP[$N]=$IDX

    "$SCRIPT_DIR/run_camera_experiment.sh" "$N" 2>&1 | tee -a "$LOG"
    echo "" | tee -a "$LOG"

    if [[ $N -lt 4 ]]; then
        echo "Cooling down 30s before next experiment..." | tee -a "$LOG"
        sleep 30
    fi
done

echo "" | tee -a "$LOG"
echo "ALL EXPERIMENTS DONE — $(date)" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Run analysis:" | tee -a "$LOG"

ANALYZE_CMD="python3 experiments/analyze_cameras.py \\"
for N in 1 2 3 4; do
    IDX="${SESSION_MAP[$N]}"
    ANALYZE_CMD+=$'\n'"    sessions/session${IDX}.jsonl $N sessions/session${IDX}_baseline.json \\"
done
echo "${ANALYZE_CMD%\\}" | tee -a "$LOG"
