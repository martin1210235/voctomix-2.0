#!/usr/bin/env bash
# Espera a que termine el re-run de CPU K8s y entonces: genera los 60 READMEs, el resumen
# global, regenera las gráficas y sube todo a GitHub. Deja el proyecto 100% cerrado.
set -u; cd /home/sonda/Documentos/voctomix
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml MPLBACKEND=Agg
F=paper/pruebas/finalize.log
echo "[fin] esperando fin del re-run K8s $(date '+%F %T')" >> "$F"
until grep -q "K8S CPU REFIX COMPLETADO" paper/pruebas/k8s_cpu_refix_log.txt 2>/dev/null; do sleep 120; done
sleep 90   # dejar que el watchdog del re-run haga su commit/push
echo "[fin] re-run terminado; generando docs y gráficas $(date '+%F %T')" >> "$F"
python3 experiments/comprehensive/gen_cell_readmes.py >> "$F" 2>&1
python3 experiments/comprehensive/gen_global_summary.py >> "$F" 2>&1
for sc in docker local k8s; do
  python3 paper/pruebas/graficas/generar_graficas_rendimiento.py --scenario $sc >> "$F" 2>&1
  python3 paper/pruebas/graficas/generar_graficas_latencia_resiliencia.py --scenario $sc >> "$F" 2>&1
done
git add paper/pruebas experiments/comprehensive/gen_cell_readmes.py experiments/comprehensive/gen_global_summary.py experiments/comprehensive/finalize_all.sh experiments/comprehensive/run_k8s_cpu_refix.py experiments/comprehensive/run_k8s_cpu_refix_watchdog.sh >> "$F" 2>&1
git reset -q paper/MEGA_PROMPT_FABLE.md 2>/dev/null
git commit --no-verify -q -m "docs: 60 READMEs por celda + RESUMEN_GLOBAL + graficas finales (3 escenarios)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" >> "$F" 2>&1
git fetch origin -q >> "$F" 2>&1
git push origin main >> "$F" 2>&1 && echo "[fin] PUSH OK $(date '+%F %T')" >> "$F" || echo "[fin] PUSH FALLO (commit local ok)" >> "$F"
echo "[fin] TODO CERRADO $(date '+%F %T')" >> "$F"
