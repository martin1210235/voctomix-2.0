#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/experiment_run.log"

echo "Starting all camera experiments — $(date)" | tee "$LOG"
echo "Logs: $LOG"
echo ""

for N in 1 2 3 4; do
    echo "========================================" | tee -a "$LOG"
    echo "  Experiment N=$N — $(date)" | tee -a "$LOG"
    echo "========================================" | tee -a "$LOG"
    "$SCRIPT_DIR/run_camera_experiment.sh" "$N" 2>&1 | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    echo "Cooling down 15s before next experiment..." | tee -a "$LOG"
    sleep 15
done

echo "ALL EXPERIMENTS DONE — $(date)" | tee -a "$LOG"
echo "Run analysis:" | tee -a "$LOG"
echo "  python3 experiments/analyze_cameras.py \\" | tee -a "$LOG"
echo "    sessions/session1.jsonl 1 \\" | tee -a "$LOG"
echo "    sessions/session2.jsonl 2 \\" | tee -a "$LOG"
echo "    sessions/session3.jsonl 3 \\" | tee -a "$LOG"
echo "    sessions/session4.jsonl 4" | tee -a "$LOG"
