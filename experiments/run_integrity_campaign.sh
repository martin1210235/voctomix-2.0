#!/usr/bin/env bash
# Drives the output-integrity campaign (reviewer point R2.1) across the four
# video profiles of one deployment tier, reusing the exact bring-up method of the
# original campaign documented in paper/pruebas/RUNBOOK.md:
#   docker -> docker-compose.experiment.yml (BBB master, colour-marked cameras)
#   local  -> experiments/comprehensive/local_scenario.sh
#   k8s    -> k8s_escenario/experiments/k8s_scenario.sh
#
# The "experiment" profile is used deliberately: it is the same load that
# produced the CPU figures reported in the paper, so frame integrity and CPU
# refer to the same working point.
#
# Usage:
#   ./run_integrity_campaign.sh <docker|local|k8s> [reps] [duration_s] [freshness_window_s]
#
# Results are appended to output_integrity_results/output_integrity.csv.

set -u

TIER="${1:?tier required: docker | local | k8s}"
REPS="${2:-3}"
DUR="${3:-60}"
FRESH_WIN="${4:-10}"

STACK_ROOT="/home/sonda/Documentos/voctomix"            # working tree with videos + stack
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS="${SELF_DIR}/output_integrity_results"
MEASURE="${SELF_DIR}/measure_output_integrity.sh"
COMP="${STACK_ROOT}/experiments/comprehensive"
K8S="${STACK_ROOT}/k8s_escenario/experiments/k8s_scenario.sh"
WARMUP=35

mkdir -p "${RESULTS}"

fps_of() { case "$1" in *p25) echo 25 ;; *p50) echo 50 ;; esac; }

teardown() {
    case "${TIER}" in
        docker) (cd "${STACK_ROOT}" && docker compose -f docker-compose.yml \
                    -f docker-compose.experiment.yml down >/dev/null 2>&1) ;;
        local)  bash "${COMP}/local_scenario.sh" down >/dev/null 2>&1 ;;
        k8s)    bash "${K8S}" down >/dev/null 2>&1 ;;
    esac
}

sources_up() {   # echoes how many of the four cameras are live
    case "${TIER}" in
        docker) docker ps --filter health=healthy --format '{{.Names}}' \
                    | grep -cE '^cam[1-4]$' ;;
        local)  pgrep -fc 'voctolocal_cam[1-4]' 2>/dev/null || echo 0 ;;
        k8s)    kubectl get pods -n voctomix-exp --no-headers 2>/dev/null \
                    | grep -E '^cam[1-4]-' | grep -c Running ;;
    esac
}

# A native voctocore left behind by an earlier experiment keeps ports 9999 and
# 11000, and the Docker stack then silently stays in "Created" with zero sources,
# which is how an entire run can be lost without any error being raised.
preflight() {
    if ss -lnt 2>/dev/null | grep -qE ':(9999|11000)\b'; then
        echo "    [preflight] ports busy; clearing stale processes"
        pkill -f 'voctocore\.py' 2>/dev/null
        pkill -f 'voctolocal_|voctoraw|voctosynth' 2>/dev/null
        sleep 5
    fi
    if ss -lnt 2>/dev/null | grep -qE ':(9999|11000)\b'; then
        echo "[ABORT] ports 9999/11000 still busy after cleanup" | tee -a "${RESULTS}/campaign.log"
        return 1
    fi
    return 0
}

bring_up() {     # $1 = format
    local fmt="$1"
    case "${TIER}" in
        docker)
            bash "${COMP}/set_format.sh" "${fmt}" >/dev/null 2>&1
            (cd "${STACK_ROOT}" && docker compose -f docker-compose.yml \
                -f docker-compose.experiment.yml up -d >/dev/null 2>&1)
            ;;
        local)
            bash "${COMP}/set_format.sh" "${fmt}" >/dev/null 2>&1
            bash "${COMP}/local_scenario.sh" base_up >/dev/null 2>&1
            for n in 1 2 3 4; do
                bash "${COMP}/local_scenario.sh" cam_up "$n" experiment >/dev/null 2>&1
            done
            ;;
        k8s)
            bash "${K8S}" up "${fmt}" >/dev/null 2>&1
            bash "${K8S}" cams "${fmt}" experiment >/dev/null 2>&1
            ;;
    esac
}

echo "=== output-integrity campaign :: tier=${TIER} reps=${REPS} dur=${DUR}s ==="
teardown

for fmt in 1080p25 1080p50 2160p25 2160p50; do
    fps="$(fps_of "${fmt}")"
    echo ""
    echo "--- ${TIER} / ${fmt} (${fps} fps) ---"
    preflight || { teardown; continue; }
    bring_up "${fmt}"

    # Wait for the four sources, then hold the documented warm-up.
    ok=0
    for _ in $(seq 1 40); do
        [ "$(sources_up)" -ge 4 ] && { ok=1; break; }
        sleep 5
    done
    if [ "${ok}" -ne 1 ]; then
        echo "[SKIP] ${TIER}/${fmt}: only $(sources_up)/4 sources came up" | tee -a "${RESULTS}/campaign.log"
        teardown
        continue
    fi
    echo "    4/4 sources up; warm-up ${WARMUP}s"
    sleep "${WARMUP}"

    for rep in $(seq 1 "${REPS}"); do
        (cd "${RESULTS}" && bash "${MEASURE}" "${TIER}_${fmt}" "${fps}" "${DUR}") \
            || echo "[WARN] ${TIER}/${fmt} rep${rep} failed" | tee -a "${RESULTS}/campaign.log"
    done

    # Content freshness is measured inside the same bring-up, so cadence and
    # content describe the same run rather than two separate deployments, and
    # repeated so the duplicate rate can be reported with its spread.
    for rep in $(seq 1 "${REPS}"); do
        (cd "${RESULTS}" && bash "${SELF_DIR}/measure_frame_freshness.sh" \
            "${TIER}_${fmt}" "${fps}" "${FRESH_WIN}") \
            || echo "[WARN] freshness ${TIER}/${fmt} rep${rep} failed" | tee -a "${RESULTS}/campaign.log"
    done

    teardown
    sleep 5
done

echo ""
echo "=== ${TIER} done ==="
