#!/usr/bin/env bash
# Smoke test de minutos del escenario K8s: versión corta de los 3 tipos de análisis
# (rendimiento con baseline 0 cams, latencia, resiliencia) para confirmar que salen
# datos válidos antes de lanzar la matriz larga.
set -u
cd /home/sonda/Documentos/voctomix
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
K8S=k8s_escenario/experiments/k8s_scenario.sh
COMP=experiments/comprehensive
S="$1/smoke_k8s"
mkdir -p "$S"

bash experiments/comprehensive/local_scenario.sh down >/dev/null 2>&1
pkill -f "python3 voctocore.py" >/dev/null 2>&1

echo "########## 1) RENDIMIENTO escalado CORTO (baseline 0 cams + 1..4) ##########"
python3 -u "$COMP/measure_performance_k8s.py" escalado "$S/1-1_escalado" \
    --format 1080p25 --idle-min 0.4 --step-min 0.4
echo "-- n_cameras_active presentes:"
awk -F, 'NR>1{print $NF}' "$S/1-1_escalado/datos.csv" 2>/dev/null | sort -u | tr '\n' ' '; echo

echo "########## 2) LATENCIA cámara CORTA (n=5) ##########"
bash "$K8S" up 1080p25 >/dev/null
bash "$K8S" cams 1080p25 latency >/dev/null
sleep 20
python3 -u "$COMP/measure_latency_camera.py" "$S/2-1_lat_camara" --n 5 --gap 2.0
echo "-- resumen latencia:"; grep latency_ms "$S/2-1_lat_camara/resumen.csv" 2>/dev/null | head -1

echo "########## 3) RESILIENCIA CORTA (n=3, crash=kubectl delete pod) ##########"
bash "$K8S" cams 1080p25 experiment >/dev/null
sleep 20
python3 -u "$COMP/measure_camera_recovery.py" "$S/3-1_resiliencia" --n 3 --gap 8 --scenario k8s
echo "-- desglose resiliencia:"
awk -F, 'NR>1{c[$NF]++} END{for(k in c) printf "%s=%d ",k,c[k]}' "$S/3-1_resiliencia/datos.csv" 2>/dev/null; echo

echo "########## limpieza ##########"
bash "$K8S" down >/dev/null
echo "SMOKE K8S FIN"
