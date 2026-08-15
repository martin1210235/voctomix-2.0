# Latency — camera switching

**Scenario:** Docker · **Format:** 1080p50 (1920×1080 @ 50 fps)
**Hardware:** Intel Core i9-10900X, 128 GB RAM, Ubuntu 22.04 (other applications closed).

## What is measured
Real (glass-to-glass) video latency when switching cameras via a hard cut, detected by colour in the mix output. 100 repetitions.

## Result
Median latency: **194.1 ms** (n=100).

## Files
`datos.csv` (raw data), `resumen.csv` (statistics), `datos.xlsx` (Excel). The output format
was verified with ffprobe (see `paper/pruebas/verificacion_formatos/`).
