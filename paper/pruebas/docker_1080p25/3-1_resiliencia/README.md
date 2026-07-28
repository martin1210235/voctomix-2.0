# Análisis 3.1 — Resiliencia: caída de una cámara y tiempo de recuperación

**Celda:** Docker · 1080p25 (1920×1080 @ 25 fps)
**Fecha:** 2026-07-25
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04

## Qué se mide
El tiempo que tarda el sistema en recuperar el feed de una cámara tras una caída, medido
sobre la salida del mix. Se descomponen tres tiempos (en ms):
- **detect** = desde la caída hasta que el feed de la víctima deja de verse.
- **restore** = desde ahí hasta que el feed vuelve a verse.
- **MTTR** = total, desde la caída hasta el feed restaurado (Mean Time To Recovery).

## Cómo se ha hecho
- Escenario: Docker (`docker-compose.yml` + `docker-compose.experiment.yml`).
- Fuentes: 4 cámaras con el máster realista Big Buck Bunny 4K (CC-BY), reescalado a 1080p25,
  cada una con un marcador de color para identificarla.
- Caída realista (`experiments/comprehensive/measure_camera_recovery.py`):
  1. Se pone la cámara víctima en pantalla completa.
  2. Se simula un crash matando su proceso ffmpeg dentro del contenedor
     (`docker exec camN pkill -9 ffmpeg`). La política de restart de Docker reinicia el
     contenedor **automáticamente** (auto-recuperación, sin intervención).
  3. Un lector de la salida del mix (puerto 11000) detecta cuándo el feed de la víctima
     desaparece y cuándo vuelve. Se registran detect, restore y MTTR.
  4. 100 iteraciones, rotando la víctima cam1→cam2→cam3→cam4.
- Comando exacto:
  ```
  experiments/comprehensive/set_format.sh 1080p25
  docker compose -f docker-compose.yml -f docker-compose.experiment.yml up -d
  python3 experiments/comprehensive/measure_camera_recovery.py \
      paper/pruebas/docker_1080p25/3-1_resiliencia --n 100 --gap 8
  ```

## Resultado (resumen; datos completos en datos.csv / datos.xlsx)
- Recuperaciones válidas: **100/100** (0 fallos; todas las cámaras se recuperaron solas).
- **MTTR** — mediana: **1794 ms** · P95: 1837 ms · rango 1717–1838 ms (± 26 ms).
- detect — mediana 758 ms · restore — mediana 1000 ms.

## Nota metodológica
La caída se provoca como crash del proceso (no `docker kill` del contenedor, que Docker no
reinicia por ser acción de usuario). La recuperación es automática por la política de restart,
que es justamente la resiliencia que aporta el despliegue en contenedores. El MTTR incluye la
latencia de salida de voctocore (~0,3 s), coherente con el resto de medidas.

## Ficheros
- `datos.csv` (100 filas: iteración, victim, detect_ms, restore_ms, mttr_ms, status),
  `resumen.csv`, `datos.xlsx`, `run.log`, `capturas/`.
