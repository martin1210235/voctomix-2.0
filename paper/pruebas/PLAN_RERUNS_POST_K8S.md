# Plan de re-ejecuciones (cuando termine K8s y la máquina esté libre)

Tareas pendientes que NO se pueden hacer mientras corre la matriz K8s (usan CPU/puertos).
Los scripts ya están preparados (baseline de 0 cámaras añadido a los drivers de Docker y Local).

## 1. Verificación de formato con ffprobe (Docker + Local, los 4 formatos)
Resuelve la incongruencia de CPU: confirma si 2160p50 corre de verdad a 3840×2160@50.
Para cada escenario y formato: levantar, `ffprobe` del mix, anotar ancho×alto@fps reales.

- **K8s**: ya verificado por celda durante la matriz (revisar `paper/pruebas/matrix_k8s_run.log`
  y los `verify-format` de cada celda). Extraer y tabular.
- **Docker** (por formato):
  ```
  experiments/comprehensive/set_format.sh <fmt>
  docker compose -f docker-compose.yml -f docker-compose.experiment.yml up -d   # esperar healthy
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate \
      -of default=noprint_wrappers=1 tcp://127.0.0.1:11000
  docker compose -f docker-compose.yml -f docker-compose.experiment.yml down
  ```
- **Local** (por formato): igual pero con `local_scenario.sh base_up` + `cam_up 1 experiment` y `down`.

## 2. Rehacer el escalado 1.1 con baseline de 0 cámaras (8 celdas: Docker×4 + Local×4)
Los drivers YA incluyen el baseline (`--idle-min 15` por defecto). Para rehacer solo el escalado
sin repetir el resto: borrar el `datos.csv` viejo y relanzar la matriz (los checkpoints saltan lo
demás), o lanzar el análisis directamente:
- **Local**: `python3 experiments/comprehensive/measure_performance_local.py escalado \
    paper/pruebas/local_<fmt>/1-1_escalado --idle-min 15 --step-min 15` (tras `set_format.sh <fmt>`).
- **Docker**: `python3 experiments/comprehensive/run_performance.py escalado \
    paper/pruebas/docker_<fmt>/1-1_escalado --idle-min 15 --step-min 15` (tras `set_format.sh <fmt>`).
- Verificar que el nuevo `datos.csv` tiene el nivel `0` cámaras con valores reales (no 0,0).
- Nota: confirmar que `parse_performance.py` (Docker) etiqueta bien el tramo de 0 cámaras.

## 3. Repetir latencia 2.2 (composición) en 2160p50 (Docker y Local) — outlier
```
set_format.sh 2160p50
# Docker: up latency stack; Local: base_up + cams latency
python3 experiments/comprehensive/measure_latency_composite.py \
    paper/pruebas/<docker|local>_2160p50/2-2_lat_composicion --n 100 --gap 2.5
```
Comparar con el valor previo (docker 334 ms, local 243 ms) para ver si era fluctuación.

## 4. Sostenida de 24 h en Docker 4K (memory-leak)
`run_performance.py sostenida paper/pruebas/docker_2160p50/1-2_sostenida_24h --duration-min 1440`
(en 1 formato representativo por escenario, al final de todo). Caracteriza la fuga de RAM.

## 5. Gráficas de K8s (preview interno)
Cuando termine la matriz K8s: `generar_graficas_rendimiento.py --scenario k8s` y
`generar_graficas_latencia_resiliencia.py --scenario k8s` (ya soportan k8s).
Y la comparativa entre escenarios (mismo formato, 3 escenarios) para el mensaje del paper.

## Orden sugerido
ffprobe-verify (rápido) → decidir sobre incongruencia CPU → escalados con baseline (8×~75min) →
latencia 2.2 (2×~5min) → gráficas → (aparte, largo) 24h Docker 4K.
