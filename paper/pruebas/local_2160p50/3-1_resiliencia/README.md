# Resilience — camera failure and recovery

**Scenario:** Local (native) · **Format:** 2160p50 (3840×2160 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
A camera failure is forced and the MTTR (detection + recovery) is measured on the mix output. 100 repetitions.

Failure/recovery mechanism: a native supervisor restarts the ffmpeg process (systemd-style).

## Result
Median MTTR: **1576.95 ms** (detection 17.2 ms + recovery 1560.5 ms), n=100.

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
