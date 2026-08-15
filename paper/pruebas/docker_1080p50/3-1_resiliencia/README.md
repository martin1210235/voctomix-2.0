# Resilience — camera failure and recovery

**Scenario:** Docker · **Format:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
A camera failure is forced and the MTTR (detection + recovery) is measured on the mix output. 100 repetitions.

Failure/recovery mechanism: docker exec camN pkill -9 ffmpeg (container restart policy).

## Result
Median MTTR: **1255.45 ms** (detection 337.05 ms + recovery 880.6 ms), n=100.

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
