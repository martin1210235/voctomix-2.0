# Análisis 2.1 — Latencia de conmutación de cámara (corte directo)

**Celda:** Docker · 1080p25 (1920×1080 @ 25 fps)
**Fecha:** 2026-07-25
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04

## Qué se mide
El tiempo, en milisegundos, desde que se ordena un cambio de cámara (corte directo)
hasta que ese cambio se ve en la salida compositada de voctocore. Es la **latencia de
vídeo real** que pidieron los tutores, no la confirmación del protocolo.

## Cómo se ha hecho
- Escenario: Docker (`docker-compose.yml` + `docker-compose.latency.yml`).
- Fuentes: 4 cámaras de **color sólido** (cam1=rojo, cam2=verde, cam3=azul, cam4=amarillo)
  a 1920×1080@25, para detectar el cambio sin ambigüedad. La latencia de conmutación es
  independiente del contenido, por eso se usan colores planos.
- Procedimiento (script `experiments/comprehensive/measure_latency_camera.py`):
  1. Se pone el programa en pantalla completa sobre cam1.
  2. Se envía `set_video_a <cam>` por el puerto de control 9999 y se marca t0.
  3. Un lector de la salida del mix (puerto **11000**) detecta el primer frame cuyo color
     ya es el de la cámara destino; ese instante es t1.
  4. latencia = t1 − t0. Se repite 100 veces, rotando cam1→2→3→4.
- Comando exacto:
  ```
  experiments/comprehensive/set_format.sh 1080p25
  docker compose -f docker-compose.yml -f docker-compose.latency.yml up -d
  python3 experiments/comprehensive/measure_latency_camera.py \
      paper/pruebas/docker_1080p25/2-1_lat_camara --n 100 --gap 2.5
  ```
- Estado del PC: aplicaciones cerradas (solo terminal + VS Code), sin otras cargas.

## Resultado (resumen; datos completos en datos.csv / datos.xlsx)
- Conmutaciones válidas: **100/100** (0 fallos).
- Mediana: **293,0 ms** · P95: 296,1 ms · P99: 297,1 ms.
- Mín–Máx: 285,7 – 297,2 ms · Media 292,8 ± 2,2 ms.

## Nota metodológica
La latencia incluye la transición por la tubería interna de voctocore (verificado: idéntica
medida en las dos salidas independientes 11000 y 12000, por lo que no es un artefacto del
lector). La precisión está acotada al periodo de frame (40 ms a 25 fps).

## Ficheros
- `datos.csv` — 100 medidas crudas (iteración, from, to, latency_ms, status).
- `resumen.csv` — estadística.
- `datos.xlsx` — lo anterior en Excel (hojas datos + resumen).
- `run.log` — traza de ejecución.
- `capturas/` — pantallazos.
