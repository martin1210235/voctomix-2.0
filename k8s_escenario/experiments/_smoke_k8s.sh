#!/usr/bin/env bash
# Few-minute smoke test of the K8s scenario: a short version of the 3 analysis
# types (performance with a 0-camera baseline, latency, resilience) to confirm
# valid data comes out before launching the full test matrix.
set -u
cd /home/sonda/Documentos/voctomix
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
K8S=k8s_escenario/experiments/k8s_scenario.sh
COMP=experiments/comprehensive
S="$1/smoke_k8s"
mkdir -p "$S"

bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
pkill -f "python3 voctocore.py" >/dev/null 2>&1

echo "########## 1) PERFORMANCE short scaling (baseline 0 cams + 1..4) ##########"
python3 -u "$COMP/measure_performance_k8s.py" escalado "$S/1-1_escalado" \
    --format 1080p25 --idle-min 0.4 --step-min 0.4
echo "-- n_cameras_active present:"
awk -F, 'NR>1{print $NF}' "$S/1-1_escalado/datos.csv" 2>/dev/null | sort -u | tr '\n' ' '; echo

echo "########## 2) CAMERA LATENCY short (n=5) ##########"
bash "$K8S" up 1080p25 >/dev/null
bash "$K8S" cams 1080p25 latency >/dev/null
sleep 20
python3 -u "$COMP/measure_latency_camera.py" "$S/2-1_lat_camara" --n 5 --gap 2.0
echo "-- latency summary:"; grep latency_ms "$S/2-1_lat_camara/resumen.csv" 2>/dev/null | head -1

echo "########## 3) RESILIENCE short (n=3, crash=kubectl delete pod) ##########"
bash "$K8S" cams 1080p25 experiment >/dev/null
sleep 20
python3 -u "$COMP/measure_camera_recovery.py" "$S/3-1_resiliencia" --n 3 --gap 8 --scenario k8s
echo "-- resilience breakdown:"
awk -F, 'NR>1{c[$NF]++} END{for(k in c) printf "%s=%d ",k,c[k]}' "$S/3-1_resiliencia/datos.csv" 2>/dev/null; echo

echo "########## cleanup ##########"
bash "$K8S" down >/dev/null
echo "SMOKE K8S DONE"
