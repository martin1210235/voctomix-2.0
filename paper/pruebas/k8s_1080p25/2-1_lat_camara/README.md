# Latency — camera switching

**Scenario:** Kubernetes · **Format:** 1080p25 (1920×1080 @ 25 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
Real (glass-to-glass) video latency when switching cameras via a hard cut, detected by colour in the mix output. 100 repetitions.

## Result
Median latency: **292.5 ms** (n=100).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
