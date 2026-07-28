# Análisis 2.2 — Latencia de conmutación de composición (fs ↔ side-by-side)

**Celda:** Docker · 1080p25 (1920×1080 @ 25 fps)
**Fecha:** 2026-07-25
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04

## Qué se mide
El tiempo, en milisegundos, desde que se ordena un cambio de modo de composición
(pantalla completa ↔ side-by-side, en corte) hasta que ese cambio se ve en la salida
del mix. Es la **latencia de vídeo real** del cambio de composición.

## Cómo se ha hecho
- Escenario: Docker (`docker-compose.yml` + `docker-compose.latency.yml`).
- Fuentes: 4 cámaras de color sólido (A=cam1 rojo, B=cam2 verde), 1920×1080@25.
- Procedimiento (`experiments/comprehensive/measure_latency_composite.py`):
  1. Se alterna con `cut fs(cam1,cam2)` y `cut sbs(cam1,cam2)` por el puerto 9999, marcando t0.
     (Nota: se usa `cut`, que hace el cambio en corte; `set_composite_mode` no aplica el cambio.)
  2. Un lector de la salida del mix (puerto 11000) muestrea el punto **centro-derecha**, que en
     pantalla completa muestra la fuente A (rojo) y en side-by-side la fuente B (verde). El primer
     frame en que ese punto pasa al color esperado marca t1.
  3. latencia = t1 − t0. 100 conmutaciones, alternando fs→sbs y sbs→fs.
- Comando exacto:
  ```
  experiments/comprehensive/set_format.sh 1080p25
  docker compose -f docker-compose.yml -f docker-compose.latency.yml up -d
  python3 experiments/comprehensive/measure_latency_composite.py \
      paper/pruebas/docker_1080p25/2-2_lat_composicion --n 100 --gap 2.5
  ```

## Resultado (resumen; datos completos en datos.csv / datos.xlsx)
- Conmutaciones válidas: **100/100** (0 fallos).
- Mediana: **296,3 ms** · P95: 297,9 ms · P99: 299,3 ms.
- Mín–Máx: 283,0 – 299,5 ms · Media 296,1 ± 1,8 ms.

## Nota metodológica
Se mide el cambio en **corte** (no la transición animada, que dura 750 ms fijos por
configuración y mediría esa constante). Coherente con la latencia de cámara (2.1). Pendiente
de confirmar con los tutores si prefieren también la transición animada.

## Ficheros
- `datos.csv`, `resumen.csv`, `datos.xlsx`, `run.log`, `capturas/`.
