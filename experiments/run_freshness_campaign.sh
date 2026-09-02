#!/usr/bin/env bash
# Frame-freshness campaign: confirms that the frames counted by the
# output-integrity campaign carry new content instead of a repeated last frame.
#
# EXPERIMENTAL DESIGN: the source material itself (Big Buck Bunny) contains some
# naturally near-identical consecutive frames, so an absolute duplicate count
# means little on its own. Each tier is therefore measured at its lightest
# profile (1080p25, far from saturation) and at its heaviest (2160p50, at the
# host limit). If the pipeline were starving its compositor at 2160p50, the
# duplicate rate would rise sharply against its own 1080p25 control; a flat
# comparison rules that failure mode out.
#
# Usage: ./run_freshness_campaign.sh [window_s] [format ...]

set -u

WIN="${1:-5}"
shift || true
FORMATS=("$@")
[ ${#FORMATS[@]} -eq 0 ] && FORMATS=(1080p25 2160p50)
STACK_ROOT="/home/sonda/Documentos/voctomix"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS="${SELF_DIR}/output_integrity_results"
COMP="${STACK_ROOT}/experiments/comprehensive"
K8S="${STACK_ROOT}/k8s_escenario/experiments/k8s_scenario.sh"
mkdir -p "${RESULTS}"

teardown_all() {
    (cd "${STACK_ROOT}" && docker compose -f docker-compose.yml \
        -f docker-compose.experiment.yml down >/dev/null 2>&1)
    bash "${COMP}/local_scenario.sh" down >/dev/null 2>&1
    bash "${K8S}" down >/dev/null 2>&1
}

sources_up() {
    case "$1" in
        docker) docker ps --filter health=healthy --format '{{.Names}}' | grep -cE '^cam[1-4]$' ;;
        local)  pgrep -fc 'voctolocal_cam[1-4]' 2>/dev/null || echo 0 ;;
        k8s)    kubectl get pods -n voctomix-exp --no-headers 2>/dev/null | grep -E '^cam[1-4]-' | grep -c Running ;;
    esac
}

bring_up() {   # $1 tier, $2 format
    case "$1" in
        docker)
            bash "${COMP}/set_format.sh" "$2" >/dev/null 2>&1
            (cd "${STACK_ROOT}" && docker compose -f docker-compose.yml \
                -f docker-compose.experiment.yml up -d >/dev/null 2>&1) ;;
        local)
            bash "${COMP}/set_format.sh" "$2" >/dev/null 2>&1
            bash "${COMP}/local_scenario.sh" base_up >/dev/null 2>&1
            for n in 1 2 3 4; do
                bash "${COMP}/local_scenario.sh" cam_up "$n" experiment >/dev/null 2>&1
            done ;;
        k8s)
            bash "${K8S}" up "$2" >/dev/null 2>&1
            bash "${K8S}" cams "$2" experiment >/dev/null 2>&1 ;;
    esac
}

teardown_all
for tier in docker local k8s; do
    for fmt in "${FORMATS[@]}"; do
        case "${fmt}" in *p50) fps=50 ;; *) fps=25 ;; esac
        echo ""
        echo "--- freshness :: ${tier} / ${fmt} ---"
        bring_up "${tier}" "${fmt}"
        ok=0
        for _ in $(seq 1 40); do
            [ "$(sources_up "${tier}")" -ge 4 ] && { ok=1; break; }
            sleep 5
        done
        if [ "${ok}" -ne 1 ]; then
            echo "[SKIP] ${tier}/${fmt}: sources did not come up" | tee -a "${RESULTS}/campaign.log"
            teardown_all; continue
        fi
        sleep 35
        (cd "${RESULTS}" && bash "${SELF_DIR}/measure_frame_freshness.sh" \
            "${tier}_${fmt}" "${fps}" "${WIN}") \
            || echo "[WARN] freshness ${tier}/${fmt} failed" | tee -a "${RESULTS}/campaign.log"
        teardown_all
        sleep 5
    done
done
echo ""
echo "=== freshness campaign done ==="
