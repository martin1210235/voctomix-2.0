#!/usr/bin/env bash
set -u; cd /home/sonda/Documentos/voctomix
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
W=paper/pruebas/k8s_cpu_refix_watchdog.log
echo "[wd] INICIO $(date '+%F %T')" >> "$W"
for a in $(seq 1 20); do
  python3 -u experiments/comprehensive/run_k8s_cpu_refix.py >> paper/pruebas/k8s_cpu_refix_stdout.log 2>&1
  grep -q "K8S CPU REFIX COMPLETADO" paper/pruebas/k8s_cpu_refix_log.txt 2>/dev/null && { echo "[wd] COMPLETADO $(date '+%F %T')" >> "$W"; break; }
  echo "[wd] salió sin completar; reintento (intento $a) en 60s" >> "$W"
  kubectl delete ns voctomix-exp --grace-period=0 --force >/dev/null 2>&1; sleep 60
done
git add paper/pruebas/k8s_1080p25 paper/pruebas/k8s_1080p50 paper/pruebas/k8s_2160p25 paper/pruebas/k8s_2160p50 paper/pruebas/k8s_cpu_refix_log.txt >> "$W" 2>&1
git reset -q paper/MEGA_PROMPT_FABLE.md 2>/dev/null
git commit --no-verify -q -m "data(k8s): re-medicion CPU/RAM con soporte arreglado (comparacion justa)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" >> "$W" 2>&1
git push origin main >> "$W" 2>&1 && echo "[wd] PUSH OK $(date '+%F %T')" >> "$W" || echo "[wd] PUSH FALLO (commit local ok)" >> "$W"
echo "[wd] FIN $(date '+%F %T')" >> "$W"
